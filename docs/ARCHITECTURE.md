# Architecture and Design Decisions

## Overview

ChoopScoop is a Playwright-powered site auditor that detects marketing tags, analytics
platforms, and web technologies across crawled pages. It runs headless Chromium to render
JavaScript-heavy sites, then applies regex and URL-signature matching against the rendered
DOM, network requests, meta tags, and response headers.

```
CLI (cli.py)
  |
  v
SiteAuditor (auditor.py)
  |-- Playwright browser (headless Chromium)
  |-- Pattern matching engine
  |     |-- TAG_PATTERNS (73 marketing/analytics tags)
  |     |-- TECHNOLOGY_PATTERNS (50 platform fingerprints)
  |     |-- GA4_EVENTS (25 dataLayer event types)
  |     `-- Response header rules
  |-- Link extraction and crawl queue
  `-- Export (JSON / CSV / HTML)
```

## Key Design Decisions

### Built-in detection over Wappalyzer

Early versions shelled out to `wappalyzer-next` (the npm CLI) as a subprocess for
technology detection. This was dropped in v3.0 for three reasons:

1. **Licensing conflict.** wappalyzer-next is GPL v3; ChoopScoop is MIT. Distributing
   them together creates a license compatibility issue.
2. **Performance.** Spawning a Node subprocess per page added 2-4 seconds of overhead
   on top of the Playwright crawl. Built-in regex matching against already-fetched HTML
   is effectively free.
3. **Reliability.** The subprocess introduced a hard dependency on Node.js and npm, plus
   version-specific bugs. Removing it means the only runtime dependency is Python +
   Playwright.

The trade-off is maintaining patterns manually, but for the MarTech/analytics domain this
is manageable -- the tag ecosystem changes slowly and the patterns are straightforward
(CDN hostnames, SDK init calls, meta generator tags).

### domcontentloaded over networkidle

Playwright's `goto()` supports several wait strategies. The original code used
`networkidle` (wait until no network connections for 500ms), which sounds ideal for
capturing all tag-firing activity. In practice, modern sites with analytics pixels,
chat widgets, websockets, and ad exchanges never reach network idle -- the page times
out at 30 seconds.

The current approach:

1. Wait for `domcontentloaded` (fast, reliable -- the HTML is parsed and scripts are
   loaded).
2. Best-effort `networkidle` with a 5-second timeout. If it settles, great. If not,
   proceed with what we have.

This captures the vast majority of tags because marketing scripts typically fire within
1-2 seconds of DOM ready. The few that load later (lazy-loaded chat widgets, deferred
pixels) are still caught if they appear in the static HTML source.

### Dual detection strategy: patterns + URL signatures

Each tag entry supports two detection methods:

- **Regex patterns** match against the full page HTML (e.g., `GTM-[A-Z0-9]{4,}` for
  Google Tag Manager container IDs).
- **URL signatures** match against the page source as substring checks (e.g.,
  `js.hs-scripts.com` for HubSpot).

Using both reduces false negatives. Some tags are only identifiable by their script URL
(no distinctive runtime pattern), while others are injected inline without a recognizable
URL. The URL check is a simple `in` operation, not a regex, which keeps it fast across
73 patterns times hundreds of pages.

### Technology detection via response headers

CMS and platform detection originally relied only on HTML patterns and meta tags. This
misses server-side technologies that leave no trace in the DOM. v3.0 added header-based
detection:

- `server: nginx` / `server: Apache` / `server: cloudflare`
- `x-powered-by: PHP` / `x-powered-by: ASP.NET`
- `x-vercel-id` / `x-nf-request-id` (Netlify)
- `via: CloudFront` / `x-amz-cf-id`

Headers are checked with the same regex engine as HTML patterns, using a separate
`headers` field in `TECHNOLOGY_PATTERNS` entries.

### Crawl state and resume

Long crawls (100+ pages) can fail mid-run due to network issues, rate limiting, or
resource constraints. The `CrawlState` class persists visited URLs, the remaining queue,
and collected page data to a JSON file. On restart, the auditor picks up where it left
off instead of re-crawling.

State files are domain-specific (`crawl_state_example_com.json`) so multiple audits can
coexist. The `--no-resume` flag forces a fresh start.

### Why not async HTTP (httpx/aiohttp) instead of Playwright?

Many tag detection tools use plain HTTP requests. ChoopScoop uses a real browser because:

- **JavaScript rendering.** Most marketing tags are injected by JavaScript (GTM, HubSpot,
  Segment). A plain HTTP fetch sees none of them.
- **DataLayer access.** GA4 events are pushed to `window.dataLayer` at runtime. Extracting
  them requires JS execution.
- **Network request logging.** Playwright can intercept outbound requests to tracking
  domains, providing evidence of tag firing beyond pattern matching.

The cost is higher resource usage and slower crawl speed. For the typical use case
(auditing a single site, 50-500 pages), this is an acceptable trade-off.

## Project Layout

```
src/choopscoop/
  __init__.py        # Package version
  __main__.py        # python -m choopscoop entry point
  auditor.py         # SiteAuditor class, crawl logic, export
  cli.py             # Argument parsing, config loading, dependency checks
  patterns.py        # TAG_PATTERNS, TECHNOLOGY_PATTERNS, GA4_EVENTS

tests/
  conftest.py        # Shared fixtures (config, auditor instance)
  test_tag_detection.py
  test_technology_detection.py
  test_datalayer.py
  test_url_handling.py
  test_config.py
  test_export.py
  test_patterns.py
```

Tests cover all non-Playwright logic (pattern matching, config loading, URL filtering,
data export). The browser-dependent crawl path is tested via live runs rather than mocked
browser sessions, keeping tests fast and deterministic.
