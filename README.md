# ChoopScoop

[![CI](https://github.com/JerushaGray/ChoopScoop/actions/workflows/ci.yml/badge.svg)](https://github.com/JerushaGray/ChoopScoop/actions/workflows/ci.yml)
[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE.md)
[![Playwright](https://img.shields.io/badge/browser-Playwright-45ba63.svg)](https://playwright.dev/python/)

A Playwright-powered site auditor that crawls websites to detect marketing tags, identify technologies, parse dataLayer events, and generate structured reports. Built for marketing operations professionals who need visibility into what is actually firing on a site, not just what should be.

## What it detects

| Category | Count | Examples |
|----------|-------|---------|
| Marketing/analytics tags | 73 | GTM, GA4, Facebook Pixel, LinkedIn, TikTok, Adobe, HubSpot, Segment |
| Technologies | 50 | WordPress, Shopify, React, Next.js, Cloudflare, Stripe, Vercel |
| GA4 event types | 25 | purchase, add_to_cart, page_view, generate_lead, form_submit |

All detection uses built-in pattern matching against HTML, script sources, meta tags, and response headers. No external services or API keys required.

## Quick start

```bash
# Clone and install
git clone https://github.com/JerushaGray/ChoopScoop.git
cd ChoopScoop
pip install .

# Install the Chromium browser engine (one-time)
playwright install chromium

# Run an audit
choopscoop https://example.com
```

## Usage

```bash
# Basic crawl (100 pages, depth 3, exports JSON + CSV + HTML)
choopscoop https://example.com

# Larger crawl with higher concurrency
choopscoop https://example.com --max-pages 500 --concurrent 5

# Single format output
choopscoop https://example.com --format html --output my-report

# Filter URLs
choopscoop https://example.com --exclude "/admin.*" "/login.*"

# Use a config file for repeatable settings
choopscoop https://example.com --config config.yaml

# Also works as a module
python -m choopscoop https://example.com
```

## Output

Every audit produces up to three export files:

| Format | File | Contents |
|--------|------|----------|
| JSON | `site-audit.json` | Full crawl data: tags, technologies, dataLayer, performance, network requests |
| CSV | `site-audit.csv` | One row per page with tag presence, load time, link counts |
| HTML | `site-audit.html` | Interactive dashboard with tag/tech summaries, broken links, page details |

## How it works

```
URL --> Playwright (Chromium, headless)
         |
         |--> Extract script tags, meta tags, response headers
         |--> Match against 73 tag patterns (regex + URL signatures)
         |--> Match against 50 technology patterns (HTML, meta, headers)
         |--> Parse dataLayer for GA4/ecommerce events
         |--> Capture performance metrics (load time, FCP, DOM timings)
         |--> Extract internal links --> queue for next depth level
         |
         |--> Concurrent page processing (configurable, 1-10 pages)
         |--> Retry with backoff on timeouts and server errors
         |--> Periodic flush to disk for memory management
         |--> Resume capability via state files
         |
         v
    JSON / CSV / HTML reports
```

## Project structure

```
src/choopscoop/
    __init__.py       Package metadata and version
    __main__.py       python -m choopscoop entry point
    auditor.py        SiteAuditor class: crawling, detection, export
    cli.py            Argument parsing, config loading, entry point
    patterns.py       Tag patterns, technology patterns, GA4 event map
config.yaml           Default configuration template
tests/                Test suite (pytest)
docs/
    CONTRIBUTING.md   Development guidelines
    ROADMAP.md        Planned enhancements
```

## Configuration

Copy and edit `config.yaml` to customize crawl behavior. Key settings:

```yaml
crawl:
  max_pages: 100        # Page limit
  max_depth: 3          # Link-follow depth
  rate_limit: 1.0       # Seconds between requests
  concurrent_pages: 3   # Parallel page limit (1-10)

filters:
  exclude_patterns: ["/admin.*", "/api/.*"]
  skip_extensions: [".pdf", ".jpg", ".png", ".zip"]

output:
  formats: ["json", "csv", "html"]
  prefix: "site-audit"

resume:
  enabled: true         # Resume interrupted crawls
```

All settings can also be overridden via CLI flags. See `choopscoop --help`.

## Comparison

| Feature | ChoopScoop | Screaming Frog | Lighthouse | python-seo-analyzer |
|---------|-----------|----------------|------------|---------------------|
| Marketing tag detection (73 tools) | Yes | No | No | No |
| Technology fingerprinting (50 techs) | Yes | Limited | No | No |
| DataLayer/GA4 event parsing | Yes | No | No | No |
| JavaScript-rendered pages | Yes (Playwright) | Yes | Yes | No |
| Performance metrics | Yes | Yes | Yes | No |
| Concurrent crawling | Yes (1-10 pages) | Yes | Single page | Yes |
| Resume interrupted crawls | Yes | No | N/A | No |
| Interactive HTML report | Yes | Yes | Yes | Yes |
| Free/open source | Yes (MIT) | Free tier limited | Yes | Yes |
| No external dependencies | Yes | N/A | Requires Chrome | Yes |

## Requirements

- Python 3.9+
- Playwright (installed automatically via pip)
- Chromium browser engine (`playwright install chromium`)

## License

[MIT](LICENSE.md)

## Author

**Jerusha Gray** -- Marketing Operations, MarTech, and Data Strategy
