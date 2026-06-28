# Changelog

## v3.0.1

- Added 11 ecommerce/DTC tag patterns: Shopify Web Pixels, Attentive, Yotpo, Nosto, Smile.io, Rebuy, Privy, Gorgias, AfterShip, Recharge, Bold Commerce
- Total tag detection expanded from 62 to 73 patterns
- Fixed resume bug where fresh crawls would not start due to empty state being loaded
- Fixed page load timeout by switching from networkidle to domcontentloaded with best-effort networkidle fallback
- Fixed JSON export crash caused by non-serializable datetime objects in crawl data
- Fixed .gitignore encoding corruption that prevented crawl output from being ignored

## v3.0.0

**Breaking:** Full restructure from single-file script to proper Python package.

- Reorganized into `src/choopscoop/` package layout (auditor, cli, patterns modules)
- Removed Wappalyzer subprocess dependency; all detection is now built-in
- Expanded technology detection from 8 to 50 patterns (CMS, frameworks, CDN, hosting, payment, monitoring)
- Added response header analysis for server/CDN/platform fingerprinting
- Cleaned up exception hierarchy and removed unused dependencies (aiofiles, requests)
- Updated pyproject.toml with proper src layout, console_scripts, and pytest config
- Stripped internal project management docs; streamlined for public consumption

## v2.1.1

- Fixed cross-platform Playwright browser path detection (Windows/macOS/Linux)
- Dependency checks no longer produce false errors on Windows

## v2.1.0

Initial public release.

- Playwright-powered async crawler with concurrent page processing
- 48 marketing/analytics tag detection patterns
- DataLayer extraction and GA4 event parsing
- Performance metrics (load time, FCP, DOM timings)
- Resume capability for interrupted crawls
- JSON, CSV, and HTML export
- YAML configuration support
- Cross-platform support (Windows, macOS, Linux)
