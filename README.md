#  ChoopScoop — Site Auditor & Tag Detection Tool (v2.1)

**ChoopScoop** is a professional-grade, Playwright-powered web auditing and tag detection tool.  
Developed by **Jerusha Gray** as part of her **MarTech and Data Strategy portfolio**, under **IdeoPraxis Collective LLC — DBA GetFunnelCaked**.

---

## Overview

ChoopScoop automates the auditing of websites to detect analytics and marketing tags, identify underlying technologies, analyze dataLayer events, and generate structured reports.  
It’s designed for accuracy, transparency, and performance — ideal for marketing operations professionals, analysts, and engineers who want actionable insights into digital ecosystems.

Version **2.1 (MVP)** focuses on stability, accuracy, and scalability, setting the foundation for future visualization and compliance modules.

---

##  Key Features

- **Modern Playwright crawler** with asynchronous performance  
- **Comprehensive tag detection:** GA4, GTM, Facebook, LinkedIn, TikTok, Adobe, Segment, and more  
- **DataLayer analysis:** Automatically parses GA4 and ecommerce events  
- **Performance metrics:** Load time, first contentful paint, DOM timings  
- **Cross-platform:** Works on macOS, Windows, and Linux  
- **Clean exports:** JSON, CSV, and an interactive HTML dashboard  
- **Resumable crawls:** State management for large audits  
- **Low memory footprint:** Smart flush-to-disk and batch processing

---

##  Installation

### Option 1 — Install from Source
```bash
git clone https://github.com/<your-handle>/choopscoop.git
cd choopscoop
pip install -r requirements_v2.txt
bash install_v2.1.sh
```

### Option 2 — Install via pip (recommended)
Once published or locally packaged:

```bash
pip install .
```

---

##  Post-Install Setup

After installation, run this once to install Playwright browsers (required for audits):

```bash
choopscoop setup
```

This step ensures the Chromium browser engine is properly configured.

---

##  Usage

### Basic Example
```bash
choopscoop https://example.com
```

### With Options
```bash
choopscoop https://example.com --max-pages 200 --max-depth 3 --format all
```

### From Config
You can also define settings in `config.yaml` for reusable crawl parameters.

---

## Outputs

ChoopScoop automatically generates three export formats:

| Format | File | Description |
|---------|------|-------------|
| JSON | `site-audit.json` | Full crawl data including tags, technologies, and metrics |
| CSV | `site-audit.csv` | Summarized audit metrics |
| HTML | `site-audit.html` | Interactive dashboard for visual review |

---

## 📁 Project Structure

```
choopscoop/
├── choopscoop_site_auditor_v2_1.py
├── tag_patterns.py
├── config.yaml
├── requirements_v2.txt
├── install_v2.1.sh
├── LICENSE.md
├── ROADMAP.md
├── CONTRIBUTING.md
└── docs/
    ├── DELIVERY-SUMMARY-v2.1.md
    ├── PATCH-NOTES-v2.1.md
    ├── VERSION-COMPARISON.md
    └── QUICK-START-v2.1.md
```

---

##  Roadmap

ChoopScoop evolves thoughtfully — see [ROADMAP.md](ROADMAP.md) for planned enhancements and version milestones.

---

## Contributing

This project is maintained as a **personal portfolio artifact**.  
However, it follows open documentation and structure standards to support long-term maintainability.  
See [CONTRIBUTING.md](CONTRIBUTING.md) for details on project principles and conventions.

---

##  Author

**Jerusha Gray**  
Marketing Operations, MarTech & Data Strategy  
IdeoPraxis Collective LLC — DBA GetFunnelCaked  

---

## 🪪 License

Licensed under the [MIT License](LICENSE.md).  
© 2025 IdeoPraxis Collective LLC — DBA GetFunnelCaked
