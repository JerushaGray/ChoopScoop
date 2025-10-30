# 🐾 ChoopScoop Changelog
### IdeoPraxis Collective LLC — DBA GetFunnelCaked

This changelog documents key milestones, improvements, and version updates for the ChoopScoop Site Auditor project.
---
### 🧩 v2.1.1 — Cross-Platform Compatibility Update
- **Fixed:** Playwright browser path detection now supports Windows, macOS, and Linux.  
- **Improved:** Dependency checks no longer produce false “browser not installed” errors on Windows systems.  
- **Impact:** Ensures smoother first-run setup and accurate environment validation across all platforms.

#### 🛠️ How to Update
1. Pull the latest version from GitHub:  
   ```bash
   git pull origin main
   ```
2. Replace your local `choopscoop_site_auditor_v2.1.py` with `choopscoop_site_auditor_v2.1_fixed.py`.  
3. Reinstall the package in editable mode to refresh dependencies:  
   ```bash
   pip install -e .
   ```
4. Verify installation by running:  
   ```bash
   python choopscoop_site_auditor_v2.1.py https://example.com
   ```
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
