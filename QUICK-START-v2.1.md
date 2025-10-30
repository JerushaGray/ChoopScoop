# 🚀 Site Auditor v2.1 - Quick Start

## What's New in v2.1?

v2.1 fixes all critical issues from v2.0:
- ✅ Works from any directory
- ✅ Graceful handling when PyYAML missing
- ✅ Pre-flight dependency checks
- ✅ Better error messages
- ✅ Memory management for large crawls
- ✅ Cross-platform compatibility
- ✅ Real-time progress bar

**TL;DR: v2.1 is production-ready. v2.0 had bugs.**

---

## Install (One-Time)

```bash
# Install Python dependencies
pip install playwright pyyaml

# Install Playwright browsers
playwright install chromium

# Install Wappalyzer (optional but recommended)
npm install -g wappalyzer
```

---

## Basic Usage

```bash
# Basic crawl
python site_auditor_v2.1.py https://example.com

# Fast crawl (5 concurrent pages)
python site_auditor_v2.1.py https://example.com --concurrent 5

# Deep crawl (500 pages)
python site_auditor_v2.1.py https://example.com --max-pages 500 --max-depth 5
```

---

## What You Get

### Three Export Files
```
site-audit.json     # Complete data
site-audit.csv      # Spreadsheet
site-audit.html     # Visual report ← Open this!
```

### Detected Information
- ✅ **50+ tracking tools** (GTM, GA4, Facebook, Adobe, etc.)
- ✅ **2,000+ technologies** (WordPress, React, Shopify, etc.)
- ✅ **Parsed dataLayer** (GA4 events, e-commerce)
- ✅ **Broken links** (404s, 500s)
- ✅ **Performance metrics** (load times)
- ✅ **Complete sitemap**

---

## Common Commands

```bash
# Exclude admin pages
python site_auditor_v2.1.py https://example.com --exclude "/admin.*" "/login.*"

# Only blog section
python site_auditor_v2.1.py https://example.com --include "/blog/.*"

# Slow, polite crawl
python site_auditor_v2.1.py https://example.com --rate-limit 2.0 --concurrent 1

# Use custom config
python site_auditor_v2.1.py https://example.com --config my-config.yaml

# Export only JSON
python site_auditor_v2.1.py https://example.com --format json
```

---

## Upgrade from v2.0

v2.1 is **100% backward compatible** with v2.0.

```bash
# Just replace the file
mv site_auditor_v2.py site_auditor_v2.py.old
cp site_auditor_v2.1.py site_auditor_v2.py

# All your v2.0 commands still work!
python site_auditor_v2.py https://example.com
```

---

## Key Features

- ⚡ **3-10x faster** with concurrent crawling
- 🔄 **Auto-resume** if interrupted  
- 🎯 **50+ tags** detected
- 📊 **Smart dataLayer** parsing
- 🔗 **Broken link** detection
- 💪 **Production-ready** error handling
- 🖥️ **Cross-platform** (Windows, Mac, Linux)
- 📦 **Memory efficient** (handles large crawls)

---

## Help

```bash
# See all options
python site_auditor_v2.1.py --help

# Check dependencies
python site_auditor_v2.1.py https://example.com
# (Runs pre-flight check automatically)
```

---

## Documentation

- **PATCH-NOTES-v2.1.md** - What was fixed from v2.0
- **README_v2.md** - Complete documentation
- **config.yaml** - Configuration options

---

## Troubleshooting

### "ModuleNotFoundError: playwright"
```bash
pip install playwright pyyaml
playwright install chromium
```

### "Wappalyzer not found"
```bash
npm install -g wappalyzer
```
Or ignore - built-in fallback patterns will be used

### "Can't write log file"
Log file is now in `~/.site-auditor/site-auditor.log` (safe location)

---

**Free alternative to:** Screaming Frog ($200/yr) • Sitebulb ($250/mo) • TagInspector ($150/mo)

**Version:** 2.1.0 - Stable Release
