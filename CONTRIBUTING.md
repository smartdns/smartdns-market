# Contributing

Contributions are reviewed through pull requests. Merging to `main` does not publish content. A maintainer publishes a GitHub Release tagged `vX.Y.Z` using three-part SemVer; SmartDNS Cloud syncs published Releases only. Public market content is free, and SmartDNS Cloud is the only supported installation and update channel.

## Packages and apps

Packages live at `packages/<type>/<slug>/` and have a `package.json` and package documentation where appropriate. The manifest uses schema version 1, an existing SmartDNS package type, localized `name` and `description` values for `en` and `zh-CN`, a minimum SmartDNS version, install data, capabilities, license, authors, category, changelog, and `files[]` entries. Fixed hosted files use path, byte size, and SHA-256; supported live data subscriptions use a URL descriptor with `type: "url"`, a logical path, and an HTTPS URL. Keep paths relative to the package directory. Do not include build hooks, generated binaries, or secrets. URL descriptors are for data subscriptions only; script source must remain fixed, reviewable hosted bytes.

Apps live one per file at `catalog/apps/<id>.json`. The app object itself is the source data; app manifests have an empty `files[]` array because Cloud creates the device payload. The app ID, manifest slug, and filename must match. App names and categories require `en` and `zh-CN`; domains must be normalized, specific, evidenced, and non-overlapping with other apps. Cite authoritative product documentation or vendor-owned hostnames in the pull request description. Public suffixes, broad shared roots, unexplained overlap, and domain count changes above 50% require resolution before merge.

## Versions and capabilities

Use three-part SemVer. Published versions are immutable: any source, install, capability, or app data change requires a higher version. Keep changelogs concise and explain capability changes. Declare only capabilities required by the package; pure data uses an empty capability list. Cloud performs the full product validator and runtime-specific review.

## Licensing and attribution

Use an SPDX license identifier and include or preserve all required upstream copyright notices in source files or package documentation. Confirm that submitted content can be redistributed under the declared license. `authors` records contribution attribution and does not assert the identity of GitHub commit authors.

## Content policy

Official repository content must not include circumvention content. This includes GFWList, proxy-node subscriptions, and presets intended to bypass network restrictions. Keep submissions within the package type's documented purpose. Do not include credentials, personal data, or user exports. State upstream licensing accurately; if it cannot be established, say it is unknown rather than assigning a presumed licence.

## Sign-off

Every commit must include a DCO sign-off line in its message, for example:

```text
Signed-off-by: Your Name <you@example.com>
```

Use `git commit -s`. A sign-off certifies the Developer Certificate of Origin terms. No CLA is required.

## Release publishing

Only maintainers publish GitHub Releases. Use a release tag matching `vX.Y.Z` and the release snapshot that Cloud will sync. Pull requests and merges to `main` are not publication events.
