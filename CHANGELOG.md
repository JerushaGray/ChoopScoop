# 🐾 ChoopScoop Changelog
### IdeoPraxis Collective LLC — DBA GetFunnelCaked

This changelog documents key milestones, improvements, and version updates for the ChoopScoop Site Auditor project.

---

## 📦 v2.1 — MVP Release
**Release Date:** October 2025

### 🚀 Features
- Core Playwright-powered crawler for JS-rendered sites
- Tag detection for GA4, GTM, Facebook, LinkedIn, TikTok, Adobe, Segment
- DataLayer event extraction and GA4 structure validation
- Performance metrics (load time, FCP, DOM timings)
- Resume functionality for interrupted crawls
- JSON, CSV, and HTML export options
- Configuration via `config.yaml`
- Cross-platform support

### 🛠 Improvements
- Optimized async concurrency to reduce memory usage
- Added fallback for missing meta tags and script integrity checks
- Enhanced URL deduplication logic

### 🐞 Fixes
- Fixed encoding bug in HTML export
- Addressed YAML parse edge cases on Windows paths
- Improved error handling for failed page navigation

---

## 🧩 Upcoming — v2.2
**Status:** In planning

### 🎯 Planned Enhancements
- Streamlined configuration UX with auto-detection
- Modular tag definition imports (YAML/JSON)
- Filtering for tag categories and event types
- Optional screenshot management
- Documentation refinements for public/portfolio release

---

## 🧭 Notes
All version history is aligned with documented milestones in [ROADMAP.md](ROADMAP.md) and [PATCH-NOTES-v2.1.md](docs/PATCH-NOTES-v2.1.md).

---

© 2025 IdeoPraxis Collective LLC — DBA GetFunnelCaked
