# Contributing

Contributions are reviewed through pull requests. Public market content is free. SmartDNS Cloud is the only supported installation and update channel.

## Packages and apps

Packages live at `packages/<type>/<slug>/` and have a `package.json`, a README, and all fixed source bytes under the package directory. The manifest uses schema version 1, an existing SmartDNS package type, localized `name` and `description` values for `en` and `zh-CN`, a minimum SmartDNS version, install data, capabilities, license, authors, category, changelog, and `files[]` entries with path, byte size, and SHA-256. Keep files relative to the package directory. Do not include build hooks, generated binaries, secrets, or remote file URLs.

Apps live one per file at `catalog/apps/<id>.json`. The app ID, manifest slug, and filename must match. App names and categories require `en` and `zh-CN`; domains must be normalized, specific, evidenced, and non-overlapping with other apps. Cite authoritative product documentation or vendor-owned hostnames in the pull request description. Public suffixes, broad shared roots, unexplained overlap, and domain count changes above 50% require resolution before merge.

## Versions and capabilities

Use three-part SemVer. Published versions are immutable: any source, install, capability, category-dependent output, or generated catalog change requires a higher version. Keep changelogs concise and explain capability changes. Declare only capabilities required by the package; pure data uses an empty capability list. Cloud performs the full product validator and runtime-specific review.

## Licensing and attribution

Use an SPDX license identifier and include or preserve all required upstream copyright notices in source files or package documentation. Confirm that submitted content can be redistributed under the declared license. `authors` records contribution attribution and does not assert the identity of GitHub commit authors.

## Content policy

Do not submit advertising blocking lists, ad-blocking scripts, or other ad-blocking content to the official repository. Security blocking lists remain out of scope until legal review is complete. Do not include credentials, personal data, or user exports.

## Sign-off

Every commit must include a DCO sign-off line in its message, for example:

```text
Signed-off-by: Your Name <you@example.com>
```

Use `git commit -s`. A sign-off certifies the Developer Certificate of Origin terms. No CLA is required.
