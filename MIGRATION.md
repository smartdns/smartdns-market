# Initial migration record

This file records the local first-import decisions. It is not a published catalog or package.

## Official Cloud packages

Migrated the three latest non-advertising packages from the read-only export dated 2026-11-24. The exported versions already use three-part SemVer and are preserved unchanged:

| Old package ID | Old version | Repository path | New version |
|---|---:|---|---:|
| `skill/answers-zh-concise` | `1.0.0` | `packages/skill/answers-zh-concise` | `1.0.0` |
| `knowledge/smartdns-troubleshooting` | `1.0.0` | `packages/knowledge/smartdns-troubleshooting` | `1.0.0` |
| `traffic_script/example-css` | `1.1.0` | `packages/traffic_script/example-css` | `1.1.0` |

Source bytes were copied from the dated export. `tools/check.py prepare` records the copied package bytes in each package manifest's `files[]` digest and size. App manifests contain the app data directly and have empty `files[]` arrays. The six official `adblock_list` packages were not migrated, per decision 7.

## App catalog candidates

Converted 28 of 33 candidate apps into one-file catalog package manifests. Five remain excluded pending narrower domain scope and evidence:

| App | Reason |
|---|---|
| `apple` | `apple.com` is a broad root covering multiple Apple services. Split into purpose-specific entries and provide domain evidence. |
| `google` | `google.com` is a broad root covering multiple Google services. Split into purpose-specific entries and provide domain evidence. |
| `microsoft` | `microsoft.com` is a broad root covering multiple products. Split into purpose-specific entries and provide domain evidence. |
| `facebook` | `facebook.com` is a broad root covering multiple Meta services. Split into purpose-specific entries and provide domain evidence. |
| `wechat` | `qq.com` covers multiple Tencent products and is too broad for this single entry. Provide narrower domains and evidence. |

The remaining candidate domains were normalized to lowercase and deduplicated. App names were supplied in English and Chinese; domain ownership evidence was not present in the candidate input and must be attached to the review PR before public publishing. Any newly discovered public suffix, cross-app overlap, or >50% count jump must be resolved before merge.

## Release publishing

Cloud syncs published GitHub Releases tagged `vX.Y.Z`; merging to `main` does not publish. A maintainer creates each Release after review.
