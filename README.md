# SmartDNS Market

This repository contains source data for the public SmartDNS Cloud market: localized app catalog entries and reviewed market packages. The catalog and packages are data; repository CI checks their structure and integrity.

Cloud reads an accepted commit from `smartdns/smartdns-market`, validates the snapshot with the product's market validator, and publishes approved package bytes with Cloud metadata and signatures. Users install and update market content only through SmartDNS Cloud. Do not download repository files into a device as a substitute for Cloud installation.

See [CONTRIBUTING.md](CONTRIBUTING.md) for package, app, version, licensing, and review rules. Migration history and entries held for review are documented in [MIGRATION.md](MIGRATION.md); it is not published market content.
