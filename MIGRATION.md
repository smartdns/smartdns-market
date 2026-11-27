# Initial migration record

This file records the local first-import decisions. It is not a published catalog or package.

## Official Cloud packages

Migrated the three latest non-advertising packages from the read-only export dated 2026-11-24. The exported versions already use three-part SemVer and are preserved unchanged:

| Old package ID | Old version | Repository path | New version |
|---|---:|---|---:|
| `skill/answers-zh-concise` | `1.0.0` | `packages/skill/answers-zh-concise` | `1.0.0` |
| `knowledge/smartdns-troubleshooting` | `1.0.0` | `packages/knowledge/smartdns-troubleshooting` | `1.0.0` |
| `traffic_script/example-css` | `1.1.0` | `packages/traffic_script/example-css` | `1.1.0` |

Source bytes were copied from the dated export. `tools/check.py prepare` records the copied package bytes in each package manifest's `files[]` digest and size. App manifests contain the app data directly and have empty `files[]` arrays.

## Adblock list migration (phase 1)

On 2026-11-27 the owner decided to migrate the six existing official adblock list IDs into this repository. The repo keeps the existing IDs, version, and install semantics. Each package has one URL descriptor at `list.txt`; upstream bytes remain dynamic and are not copied into the repository. The Cloud inventory reports version `1.0.0` for all six packages. Upstream licences are not established by that inventory and are marked unknown rather than inferred.

| Existing package ID | Cloud version | Repository path | Upstream URL | Upstream licence |
|---|---|---|---|---|
| `adblock_list/anti-ad` | `1.0.0` | `packages/adblock_list/anti-ad` | `https://anti-ad.net/easylist.txt` | Unknown |
| `adblock_list/easylist-china` | `1.0.0` | `packages/adblock_list/easylist-china` | `https://raw.githubusercontent.com/easylist/easylistchina/master/easylistchina.txt` | Unknown |
| `adblock_list/easylist` | `1.0.0` | `packages/adblock_list/easylist` | `https://easylist.to/easylist/easylist.txt` | Unknown |
| `adblock_list/adguard-tracking` | `1.0.0` | `packages/adblock_list/adguard-tracking` | `https://filters.adtidy.org/extension/ublock/filters/3.txt` | Unknown |
| `adblock_list/easyprivacy` | `1.0.0` | `packages/adblock_list/easyprivacy` | `https://easylist.to/easylist/easyprivacy.txt` | Unknown |
| `adblock_list/adguard-dns` | `1.0.0` | `packages/adblock_list/adguard-dns` | `https://adguardteam.github.io/AdGuardSDNSFilter/Filters/filter.txt` | Unknown |

The Cloud contract accepts one URL-backed file for `adblock_list`, redirects file requests to its URL, and uses `install.format: adblock` with category `ad`. Existing install names and `refresh_interval: 86400` are preserved. Repo validation checks the descriptor shape and HTTPS URL without fetching the subscription. The exact URL-to-URL ownership comparison and broader takeover behavior remain Cloud migration work; this repo change does not perform a live Cloud takeover.

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
