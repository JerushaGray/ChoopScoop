# Changelog

## v3.1.0

Evidence-based detection overhaul. Network requests are now the primary evidence
source for tag and technology detection, replacing the HTML-only approach that
caused false negatives, false positives, and event blindness.

### Added

- **Network request detection for tags.** Tags are now detected from captured
  third-party request hosts, not just inline HTML. LinkedIn Insight Tag, Google
  Ads/DoubleClick, and Facebook Pixel are now detected on sites where they fire
  only via network beacons with no inline signature.
- **Full third-party request capture.** The crawler now captures all requests to
  hosts that differ from the crawled page, replacing the previous 13-domain
  allowlist. Unknown vendors are no longer silently dropped.
- **Unidentified third-party host summary.** JSON export includes a deduplicated
  list of third-party hosts that did not match any known pattern, with request
  counts. Useful for competitive recon and privacy auditing.
- **GA4 Measurement Protocol decoder.** New `decode_ga4_collect_requests` method
  parses `google-analytics.com/g/collect` request URLs and POST bodies. Extracts
  event names (`en=`), measurement IDs (`tid=`), and event params (`ep.*`/`epn.*`).
  Deduplicates retransmissions (`_s=1` vs `_s=2`). Output stored under
  `ga4_collect_events` alongside the existing `datalayer` key.
- **gtag() argument object decoding in dataLayer parser.** `_parse_datalayer` now
  recognizes gtag() calls serialized as `{"0":"event","1":"purchase","2":{...}}`
  and routes them correctly: `event` commands go to the events list, while
  `config`/`consent`/`set`/`js`/`get` go to a new `gtag_config` summary.
- **Evidence and confidence model.** Every tag and technology detection now records
  what it matched on (`evidence` list) and a derived confidence level (`high`,
  `medium`, `low`). Evidence types: `html_pattern`, `script_url`, `request_host`,
  `request_url`, `meta`, `header`.
- **Technology detection from network requests.** Technologies with a `urls` field
  are now also matched against captured request hosts, enabling detection of
  platforms that load assets from known CDNs (e.g., Shopify via `cdn.shopify.com`).
- Added `urls` field to Shopify technology pattern for network corroboration.
- Added missing tag URL entries: `cm.g.doubleclick.net` and
  `pagead2.googlesyndication.com` for Google Ads, `platform.linkedin.com` for
  LinkedIn Insight, `facebook.com/tr` for Facebook Pixel.
- **Vendor-owned domain attribution.** Added `owned_domains` field to 22 pattern
  entries (16 tags, 6 technologies) listing registrable domains each vendor serves
  from. The unidentified third-party hosts bucket now excludes hosts attributable
  to a known vendor (e.g., `secure.quantserve.com` is attributed to Quantcast, not
  listed as unidentified). Only genuinely unknown vendors remain in the bucket.
- **Programmatic-Advertising tag category.** 4 new tags for ad-tech supply chain
  vendors: LiveRamp/Pippio (`rlcdn.com`, `pippio.com`), Index Exchange
  (`casalemedia.com`), PubMatic (`pubmatic.com`), Magnite/Rubicon Project
  (`rubiconproject.com`). Total tag count: 77.
- 42 new tests covering network detection, GA4 decoding, gtag argument parsing,
  false-positive hardening, evidence model, and host classification. Total: 204.

### Fixed

- **Magento false positives.** Bare `Magento` regex (case-insensitive) matched any
  text mention. Replaced with specific patterns: `Magento_Ui`, `mage/cookies`,
  `/skin/frontend/.*Magento`. Removed overly broad `/static/version` pattern.
- **WooCommerce false positives.** Bare `woocommerce` regex matched blog text.
  Replaced with `wc-cart-fragments`, `class="woocommerce`, and
  `wp-content/plugins/woocommerce`.
- **Bootstrap false positives.** CSS class pattern (`container`, `row`, `col-md`)
  matched nearly every site. Removed; kept only versioned filename pattern.
- **Tailwind false positives.** CSS utility class pattern (`flex`, `grid`,
  `text-sm`) matched nearly every site. Removed; kept only filename patterns.
  Added `detection_note` flagging that purged/bundled Tailwind is undetectable.
- **900 "unknown" dataLayer events** on gtag-heavy sites were actually gtag()
  argument objects. Now decoded correctly, with conversion events surfaced and
  config commands routed separately. Also fixed gtag argument detection for objects
  with GTM-injected non-numeric keys (e.g., `gtm.uniqueEventId`) that previously
  prevented recognition of `gtag('js', ...)` init calls.
- **POST data capture.** `log_request` now captures `request.post_data` on POST
  requests (guarded against Playwright exceptions), enabling GA4 collect request
  body parsing.

### Changed

- `detect_tags` signature: added optional `network_requests` parameter.
- `detect_technologies` signature: added optional `network_requests` parameter.
- `_parse_datalayer` return structure: added `gtag_config` key.
- JSON export: raw `network_requests` stripped from per-page data; replaced with
  top-level `matched_requests` and `unidentified_third_party_hosts` keys.
- Host-based URL matching uses `urllib.parse.urlparse` instead of substring
  matching to avoid false matches on short patterns.

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
