#!/usr/bin/env python3
"""Small standard-library checker for the SmartDNS market data repository."""
import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
TYPES = {"adblock_list", "app_template", "traffic_script", "knowledge", "skill", "config_script", "schedule", "config_bundle"}
SEMVER = re.compile(r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?$")
ID = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
DOMAIN = re.compile(r"^(?=.{1,253}$)(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?)(?:\.(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?))+$")
# Deliberately conservative public suffix list for the supplied ASCII catalog.
PUBLIC_SUFFIXES = {"com", "net", "org", "edu", "gov", "mil", "int", "io", "cn", "uk", "de", "fr", "jp", "kr", "au", "nz", "ca", "us", "ru", "in", "br", "hk", "tw", "sg", "my", "id", "vn", "th", "tr", "es", "it", "nl", "se", "no", "fi", "ch", "at", "pl", "ua", "mx", "ar", "za", "info", "biz", "xyz", "app", "dev", "me", "tv", "co", "top", "site", "online", "tech", "cloud", "pro", "name", "museum", "arpa", "中国", "公司", "网络", "co.uk", "org.uk", "ac.uk", "gov.uk", "com.cn", "net.cn", "org.cn", "gov.cn", "com.au", "net.au", "org.au", "co.jp", "co.kr", "com.hk", "com.tw", "com.sg", "com.my", "co.nz", "co.in"}
def too_broad_domains():
    try:
        policy = read_json(ROOT / "policy/domain-review.json")
        return {item["domain"] for item in policy.get("too_broad_domains", [])}
    except Exception:
        return set()


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def dump_bytes(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def manifest_paths():
    return sorted(ROOT.glob("packages/*/*/package.json")) + sorted(ROOT.glob("catalog/apps/*.json"))


def safe_file(base, rel):
    if not isinstance(rel, str) or not rel or "\\" in rel:
        raise ValueError("path must be a non-empty POSIX relative path")
    p = PurePosixPath(rel)
    if p.is_absolute() or any(part in ("", ".", "..") for part in p.parts):
        raise ValueError("absolute, empty, dot, or parent path component")
    target = base.joinpath(*p.parts)
    cursor = base
    for part in p.parts:
        cursor = cursor / part
        if cursor.is_symlink():
            raise ValueError("symlink path is forbidden")
    if not target.is_file():
        raise ValueError("file does not exist")
    return target


def generated_catalog(appdoc):
    app = appdoc["app"]
    categories = read_json(ROOT / "catalog/categories.json")
    payload = {"categories": categories, "apps": [{
        "id": app["id"], "name": app["names"]["en"], "names": app["names"],
        "vendor": app["vendor"], "category": app["category"], "icon": app["icon"],
        "domains": app["domains"],
    }]}
    return dump_bytes(payload)


def prepare():
    errors = []
    for mp in manifest_paths():
        try:
            data = read_json(mp)
            is_app = mp.parent == ROOT / "catalog/apps"
            base = ROOT / "catalog/apps" / mp.stem if is_app else mp.parent
            if is_app:
                generated = generated_catalog(data)
                out = base / "generated/catalog.json"
                out.parent.mkdir(parents=True, exist_ok=True)
                out.write_bytes(generated)
                items = [{"path": "generated/catalog.json", "size": len(generated), "sha256": hashlib.sha256(generated).hexdigest()}]
            else:
                items = []
                for file in sorted(base.rglob("*")):
                    if file.is_file() and file.name != "package.json" and not file.is_symlink():
                        rel = file.relative_to(base).as_posix()
                        b = file.read_bytes()
                        items.append({"path": rel, "size": len(b), "sha256": hashlib.sha256(b).hexdigest()})
            data["files"] = items
            mp.write_bytes(dump_bytes(data))
        except Exception as exc:
            errors.append(f"{mp.relative_to(ROOT)}: {exc}")
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print(f"Prepared files[] for {len(manifest_paths())} manifests")
    return 0


def semver_tuple(value):
    match = SEMVER.fullmatch(value or "")
    return tuple(map(int, match.groups())) if match else None


def git_show(ref, path):
    try:
        return subprocess.run(["git", "show", f"{ref}:{path}"], cwd=ROOT, check=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL).stdout
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def normalize_domain(value):
    if not isinstance(value, str):
        return None
    domain = value.strip().lower().rstrip(".")
    if domain != value or not DOMAIN.fullmatch(domain):
        return None
    try:
        domain.encode("ascii")
    except UnicodeEncodeError:
        return None
    return domain


def is_public_suffix(domain):
    return domain in PUBLIC_SUFFIXES or any(domain == s for s in PUBLIC_SUFFIXES)


def validate(base_ref=None):
    errors = []
    warns = []
    manifests = manifest_paths()
    ids = {}
    apps = {}
    versions = {}
    manifest_bytes = {}
    categories = read_json(ROOT / "catalog/categories.json") if (ROOT / "catalog/categories.json").is_file() else {}
    too_broad = too_broad_domains()
    if not isinstance(categories, dict) or not categories:
        errors.append("catalog/categories.json: expected non-empty object")
        categories = {}
    for key, names in categories.items():
        if not re.fullmatch(r"[a-z0-9_]{1,32}", key):
            errors.append(f"category {key!r}: invalid key")
        if not isinstance(names, dict) or not all(isinstance(names.get(lang), str) and names[lang].strip() for lang in ("en", "zh-CN")):
            errors.append(f"category {key}: requires non-empty en and zh-CN")
    for mp in manifests:
        rel = mp.relative_to(ROOT).as_posix()
        try:
            manifest_bytes[mp] = mp.read_bytes()
            doc = read_json(mp)
        except Exception as exc:
            errors.append(f"{rel}: invalid JSON ({exc})")
            continue
        required = ("schema_version", "id", "type", "version", "name", "description", "min_smartdns_version", "install", "capabilities", "files", "license", "authors", "category", "changelog")
        missing = [key for key in required if key not in doc]
        if missing:
            errors.append(f"{rel}: missing fields {', '.join(missing)}")
            continue
        if doc["schema_version"] != 1:
            errors.append(f"{rel}: schema_version must be 1")
        kind = doc["type"]
        slug = doc["id"].split("/", 1)[-1] if isinstance(doc["id"], str) else ""
        if kind not in TYPES or doc["id"] != f"{kind}/{slug}" or not ID.fullmatch(slug):
            errors.append(f"{rel}: invalid id/type")
        if doc["id"] in ids:
            errors.append(f"{rel}: duplicate ID {doc['id']} (also {ids[doc['id']]})")
        ids[doc["id"]] = rel
        if not isinstance(doc["version"], str) or not SEMVER.fullmatch(doc["version"]):
            errors.append(f"{rel}: version must be SemVer")
        else:
            versions[doc["id"]] = doc["version"]
        for field in ("name", "description"):
            loc = doc[field]
            if not isinstance(loc, dict) or not all(isinstance(loc.get(lang), str) and loc[lang].strip() for lang in ("en", "zh-CN")):
                errors.append(f"{rel}: {field} requires non-empty en and zh-CN")
        if not isinstance(doc["min_smartdns_version"], str) or not SEMVER.fullmatch(doc["min_smartdns_version"]):
            errors.append(f"{rel}: min_smartdns_version must be SemVer")
        if not isinstance(doc["install"], dict) or not isinstance(doc["capabilities"], list):
            errors.append(f"{rel}: install must be an object and capabilities an array")
        if not isinstance(doc["authors"], list) or not doc["authors"] or not all(isinstance(author, str) and author.strip() for author in doc["authors"]):
            errors.append(f"{rel}: authors must be a non-empty array of strings")
        if doc.get("category") not in categories:
            errors.append(f"{rel}: unknown category {doc.get('category')!r}")
        if not isinstance(doc.get("license"), str) or not doc["license"].strip():
            errors.append(f"{rel}: license must be a non-empty SPDX identifier")
        if not isinstance(doc.get("changelog"), str) or not doc["changelog"].strip():
            errors.append(f"{rel}: changelog must be non-empty")
        if not isinstance(doc["files"], list) or not doc["files"]:
            errors.append(f"{rel}: files must be a non-empty array")
        seen_paths = set()
        package_base = (ROOT / "catalog/apps" / mp.stem) if mp.parent == ROOT / "catalog/apps" else mp.parent
        for item in doc.get("files", []):
            if not isinstance(item, dict) or not all(k in item for k in ("path", "size", "sha256")):
                errors.append(f"{rel}: each files[] entry needs path, size, sha256")
                continue
            path = item["path"]
            if path in seen_paths:
                errors.append(f"{rel}: duplicate file path {path}")
            seen_paths.add(path)
            try:
                target = safe_file(package_base, path)
                data = target.read_bytes()
                if not isinstance(item["size"], int) or item["size"] != len(data):
                    errors.append(f"{rel}: {path}: size mismatch")
                if not isinstance(item["sha256"], str) or not re.fullmatch(r"[0-9a-f]{64}", item["sha256"]) or item["sha256"] != hashlib.sha256(data).hexdigest():
                    errors.append(f"{rel}: {path}: sha256 mismatch/invalid")
            except Exception as exc:
                errors.append(f"{rel}: {path}: unsafe or missing file ({exc})")
        if kind == "app_template":
            app = doc.get("app")
            if not isinstance(app, dict):
                errors.append(f"{rel}: app_template requires app object")
                continue
            appid = app.get("id")
            if appid != mp.stem or doc["id"] != f"app_template/{appid}":
                errors.append(f"{rel}: app.id, manifest id, and filename must match")
            if appid in apps:
                errors.append(f"{rel}: duplicate app ID {appid}")
            apps[appid] = (rel, app, doc)
            if app.get("category") not in categories:
                errors.append(f"{rel}: unknown category {app.get('category')!r}")
            names = app.get("names")
            if not isinstance(names, dict) or not all(isinstance(names.get(lang), str) and names[lang].strip() for lang in ("en", "zh-CN")):
                errors.append(f"{rel}: app names require en and zh-CN")
            domains = app.get("domains")
            if not isinstance(domains, list) or not domains or len(domains) > 2000:
                errors.append(f"{rel}: domains must contain 1..2000 entries")
                continue
            normed = []
            for domain in domains:
                norm = normalize_domain(domain)
                if norm is None or norm != domain:
                    errors.append(f"{rel}: invalid/non-normalized domain {domain!r}")
                    continue
                if is_public_suffix(norm):
                    errors.append(f"{rel}: public suffix is forbidden: {norm}")
                if norm in too_broad:
                    errors.append(f"{rel}: too-broad root domain needs review: {norm}")
                normed.append(norm)
            if len(set(normed)) != len(normed):
                errors.append(f"{rel}: duplicate domains")
            expected = generated_catalog(doc)
            genpath = package_base / "generated/catalog.json"
            if not genpath.is_file() or genpath.read_bytes() != expected:
                errors.append(f"{rel}: generated/catalog.json missing or not deterministic")
    # App domain overlap: any shared domain or parent/child coverage is held for review.
    appids = sorted(apps)
    for i, left_id in enumerate(appids):
        left = apps[left_id][1].get("domains", [])
        for right_id in appids[i + 1:]:
            right = apps[right_id][1].get("domains", [])
            overlaps = sorted({a for a in left for b in right if a == b or a.endswith("." + b) or b.endswith("." + a)})
            if overlaps:
                errors.append(f"app domains overlap: {left_id} / {right_id}: {', '.join(overlaps)}")
    if base_ref:
        for package_id, version in versions.items():
            kind, slug = package_id.split("/", 1)
            path = f"packages/{kind}/{slug}/package.json" if kind != "app_template" else f"catalog/apps/{slug}.json"
            old_raw = git_show(base_ref, path)
            if old_raw is None or manifest_bytes.get(ROOT / path) == old_raw:
                continue
            try:
                old_doc = json.loads(old_raw)
                old_version = old_doc.get("version")
            except Exception:
                continue
            old_v, new_v = semver_tuple(old_version), semver_tuple(version)
            if old_v and new_v and new_v <= old_v:
                errors.append(f"{path}: changed manifest version {version} must increase above base {old_version}")
            if kind == "app_template":
                old_domains = old_doc.get("app", {}).get("domains", [])
                new_domains = apps.get(slug, (None, {"domains": []}, None))[1].get("domains", [])
                if old_domains and abs(len(new_domains) - len(old_domains)) / len(old_domains) > 0.5:
                    errors.append(f"{path}: domain count changed by more than 50% ({len(old_domains)} to {len(new_domains)}); review required")
    for warn in warns:
        print(f"WARN: {warn}")
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print(f"Validation failed: {len(errors)} error(s), {len(manifests)} manifests")
        return 1
    print(f"Validation passed: {len(manifests)} manifests, {len(apps)} apps, {len(categories)} categories")
    return 0


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("prepare")
    v = sub.add_parser("validate")
    v.add_argument("--base", default=None)
    args = parser.parse_args()
    return prepare() if args.command == "prepare" else validate(args.base)


if __name__ == "__main__":
    sys.exit(main())
