#!/usr/bin/env python3
"""
Site Auditor v2.1 - Professional Web Crawler & Tag Detection Tool
Fixed: Import errors, dependency checking, memory management, cross-platform compatibility,
better progress indicators, and all critical issues from v2.0
"""

import asyncio
import json
import csv
import re
import subprocess
import logging
import argparse
import sys
import os
from pathlib import Path
from urllib.parse import urljoin, urlparse
from datetime import datetime
from collections import defaultdict
from typing import Set, Dict, List, Optional, Tuple

# Fix 1: Add script directory to path for imports
script_dir = Path(__file__).parent.absolute()
sys.path.insert(0, str(script_dir))

# Fix 2: Handle missing PyYAML gracefully
try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False
    print("⚠️  Warning: PyYAML not installed. Config file support disabled.")
    print("   Install with: pip install pyyaml")
    print("   Continuing with command-line configuration only...\n")

from playwright.async_api import async_playwright, Page, Browser, TimeoutError as PlaywrightTimeout

# Import tag patterns (with better error message)
try:
    from tag_patterns import TAG_PATTERNS, GA4_EVENTS, TECHNOLOGY_PATTERNS
except ImportError as e:
    print(f"❌ Error: Cannot find tag_patterns.py in {script_dir}")
    print("   Make sure tag_patterns.py is in the same directory as this script.")
    sys.exit(1)


def check_dependencies():
    """Check if all required dependencies are available"""
    issues = []
    
    # Check Playwright
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        issues.append("Playwright not installed. Run: pip install playwright")
    
    # Check Playwright browsers
    playwright_dir = Path.home() / '.cache' / 'ms-playwright'
    if not playwright_dir.exists() or not any(playwright_dir.glob('chromium-*')):
        issues.append("Playwright browsers not installed. Run: playwright install chromium")
    
    # Check Wappalyzer (optional)
    wappalyzer_available = check_wappalyzer()
    if not wappalyzer_available:
        print("ℹ️  Note: Wappalyzer not found (optional)")
        print("   Technology detection will use built-in patterns")
        print("   For enhanced detection, install: npm install -g wappalyzer\n")
    
    if issues:
        print("❌ Missing dependencies:")
        for issue in issues:
            print(f"   • {issue}")
        return False
    
    return True


def check_wappalyzer() -> bool:
    """Check if Wappalyzer CLI is available"""
    try:
        result = subprocess.run(
            ['wappalyzer', '--version'],
            capture_output=True,
            timeout=5,
            text=True
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


class CrawlState:
    """Manages crawl state for resume capability"""
    
    def __init__(self, state_file: str):
        self.state_file = state_file
        self.state = self.load_state()
    
    def load_state(self) -> Dict:
        """Load saved crawl state"""
        if Path(self.state_file).exists():
            try:
                with open(self.state_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logging.warning(f"Could not load state file: {e}")
        return {
            'visited_urls': [],
            'to_visit': [],
            'page_data': [],
            'broken_links': []
        }
    
    def save_state(self, visited: Set[str], to_visit: List[Tuple], 
                   page_data: List[Dict], broken_links: List[Dict]):
        """Save current crawl state"""
        try:
            state = {
                'visited_urls': list(visited),
                'to_visit': to_visit,
                'page_data': page_data,
                'broken_links': broken_links,
                'last_saved': datetime.now().isoformat()
            }
            # Fix 10: Use Path for cross-platform compatibility
            state_path = Path(self.state_file)
            with open(state_path, 'w') as f:
                json.dump(state, f, indent=2)
            logging.debug(f"Saved crawl state to {self.state_file}")
        except Exception as e:
            logging.error(f"Could not save state: {e}")


class SiteAuditorV21:
    """Enhanced web crawler with comprehensive tag detection and all v2.0 fixes"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.start_url = config['start_url']
        self.base_domain = urlparse(self.start_url).netloc
        
        # Crawl settings with validation (Fix 4)
        self.max_pages = max(1, config['crawl']['max_pages'])
        self.max_depth = max(0, config['crawl']['max_depth'])
        self.rate_limit = max(0.1, config['crawl']['rate_limit'])
        
        # Fix 4: Proper concurrent validation
        concurrent = config['crawl'].get('concurrent_pages', 3)
        if not isinstance(concurrent, int) or concurrent < 1:
            logging.warning(f"Invalid concurrent_pages: {concurrent}, using default 3")
            concurrent = 3
        self.concurrent_pages = min(concurrent, 10)
        
        self.timeout = config['crawl']['timeout'] * 1000  # Convert to ms
        
        # State management
        self.visited_urls: Set[str] = set()
        self.to_visit: List[Tuple[str, int]] = [(self.start_url, 0)]
        self.page_data: List[Dict] = []
        self.broken_links: List[Dict] = []
        self.network_requests: Dict[str, List] = defaultdict(list)
        
        # Fix 8: Domain-specific state file to avoid conflicts
        if config['resume']['enabled']:
            domain_safe = self.base_domain.replace('.', '_').replace(':', '_')
            state_file = f"crawl_state_{domain_safe}.json"  # Fix 13: Not hidden
            self.state = CrawlState(state_file)
            self.load_previous_state()
        else:
            self.state = None
        
        # Statistics
        self.stats = {
            'pages_crawled': 0,
            'pages_failed': 0,
            'tags_found': defaultdict(int),
            'technologies_found': defaultdict(int)
        }
        
        # Fix 9: Memory management
        self.output_prefix = config['output']['prefix']
        self.memory_threshold = 50  # Flush to disk every 50 pages
        
        # Setup logging with better paths (Fix 12)
        self.setup_logging()
        
        # Fix 7: Check Wappalyzer early and warn
        if config['technology']['use_wappalyzer']:
            if not check_wappalyzer():
                logging.warning("Wappalyzer not available")
                logging.info("Technology detection will use fallback patterns only")
                logging.info("To enable full detection: npm install -g wappalyzer")
                config['technology']['use_wappalyzer'] = False
    
    def setup_logging(self):
        """Configure logging with safe paths"""
        log_config = self.config['logging']
        log_level = getattr(logging, log_config['level'].upper())
        
        handlers = []
        
        if log_config['console']:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(
                logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            )
            handlers.append(console_handler)
        
        if log_config['log_file']:
            # Fix 12: Use safe directory for log files
            log_dir = Path.home() / '.site-auditor'
            log_dir.mkdir(exist_ok=True)
            log_path = log_dir / log_config['log_file']
            
            try:
                file_handler = logging.FileHandler(log_path)
                file_handler.setFormatter(
                    logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
                )
                handlers.append(file_handler)
                print(f"📝 Log file: {log_path}")
            except Exception as e:
                print(f"⚠️  Could not create log file: {e}")
        
        logging.basicConfig(
            level=log_level,
            handlers=handlers,
            force=True
        )
    
    def load_previous_state(self):
        """Load previous crawl state for resume"""
        if self.state and self.state.state:
            self.visited_urls = set(self.state.state.get('visited_urls', []))
            self.to_visit = self.state.state.get('to_visit', [(self.start_url, 0)])
            self.page_data = self.state.state.get('page_data', [])
            self.broken_links = self.state.state.get('broken_links', [])
            
            if self.visited_urls:
                logging.info(f"📂 Resuming crawl: {len(self.visited_urls)} pages already visited")
    
    def save_progress(self):
        """Save crawl progress"""
        if self.state and self.config['output']['save_progress']:
            self.state.save_state(
                self.visited_urls,
                self.to_visit,
                self.page_data,
                self.broken_links
            )
    
    def flush_to_disk(self):
        """Fix 9: Periodically flush data to disk to manage memory"""
        if len(self.page_data) >= self.memory_threshold:
            temp_file = Path(f'{self.output_prefix}_partial.json')
            try:
                # Append to existing partial file
                existing_data = []
                if temp_file.exists():
                    with open(temp_file, 'r') as f:
                        existing_data = json.load(f)
                
                existing_data.extend(self.page_data)
                
                with open(temp_file, 'w') as f:
                    json.dump(existing_data, f, indent=2)
                
                logging.info(f"💾 Flushed {len(self.page_data)} pages to disk")
                self.page_data = []  # Clear memory
            except Exception as e:
                logging.error(f"Could not flush to disk: {e}")
    
    def load_partial_data(self):
        """Load partial data back from disk"""
        temp_file = Path(f'{self.output_prefix}_partial.json')
        if temp_file.exists():
            try:
                with open(temp_file, 'r') as f:
                    partial_data = json.load(f)
                self.page_data.extend(partial_data)
                temp_file.unlink()  # Delete temp file
                logging.info(f"📂 Loaded {len(partial_data)} pages from partial file")
            except Exception as e:
                logging.error(f"Could not load partial data: {e}")
    
    def should_crawl(self, url: str) -> bool:
        """Check if URL should be crawled"""
        parsed = urlparse(url)
        
        # Must be same domain
        if parsed.netloc != self.base_domain:
            return False
        
        # Check exclude patterns
        for pattern in self.config['filters']['exclude_patterns']:
            if re.search(pattern, url):
                return False
        
        # Check include patterns
        if self.config['filters']['include_patterns']:
            matched = False
            for pattern in self.config['filters']['include_patterns']:
                if re.search(pattern, url):
                    matched = True
                    break
            if not matched:
                return False
        
        # Skip file extensions
        skip_extensions = self.config['filters']['skip_extensions']
        if any(url.lower().endswith(ext) for ext in skip_extensions):
            return False
        
        return True
    
    def normalize_url(self, url: str) -> str:
        """Normalize URL"""
        parsed = urlparse(url)
        normalized = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        if parsed.query:
            normalized += f"?{parsed.query}"
        if normalized.endswith('/') and parsed.path != '/':
            normalized = normalized[:-1]
        return normalized
    
    async def extract_links(self, page: Page, current_url: str) -> Tuple[List[str], List[Dict]]:
        """Extract internal links and identify broken links"""
        internal_links = []
        broken_links = []
        
        try:
            links_data = await page.eval_on_selector_all(
                'a[href]',
                """elements => elements.map(el => ({
                    href: el.href,
                    text: el.textContent.trim(),
                    title: el.title
                }))"""
            )
            
            for link_data in links_data:
                href = link_data['href']
                
                if not href or any(href.startswith(x) for x in ['javascript:', 'mailto:', 'tel:', '#']):
                    continue
                
                absolute_url = urljoin(current_url, href)
                normalized = self.normalize_url(absolute_url)
                
                if urlparse(normalized).netloc == self.base_domain:
                    if self.should_crawl(normalized) and normalized not in self.visited_urls:
                        internal_links.append(normalized)
                
            return list(set(internal_links)), broken_links
            
        except Exception as e:
            logging.error(f"Error extracting links from {current_url}: {e}")
            return [], []
    
    def detect_tags_comprehensive(self, page_content: str, page_url: str) -> Dict:
        """Detect all tracking tags using comprehensive pattern matching"""
        detected_tags = {}
        
        for tag_name, tag_config in TAG_PATTERNS.items():
            matches = []
            found = False
            
            for pattern in tag_config['patterns']:
                found_matches = re.findall(pattern, page_content)
                if found_matches:
                    matches.extend(found_matches)
                    found = True
            
            for url_pattern in tag_config['urls']:
                if url_pattern in page_content:
                    found = True
            
            if found or matches:
                detected_tags[tag_name] = {
                    'found': True,
                    'ids': list(set(matches)) if matches else [],
                    'category': tag_config['category']
                }
                self.stats['tags_found'][tag_name] += 1
        
        return detected_tags
    
    def detect_technologies_fallback(self, page_content: str, meta_tags: List, headers: Dict) -> List[Dict]:
        """Fallback technology detection when Wappalyzer unavailable"""
        technologies = []
        
        for tech_name, tech_config in TECHNOLOGY_PATTERNS.items():
            found = False
            
            for pattern in tech_config['patterns']:
                if re.search(pattern, page_content, re.IGNORECASE):
                    found = True
                    break
            
            if 'meta' in tech_config:
                for meta_name, meta_pattern in tech_config['meta']:
                    for meta in meta_tags:
                        if meta.get('name') == meta_name and re.search(meta_pattern, meta.get('content', '')):
                            found = True
            
            if found:
                technologies.append({
                    'name': tech_name,
                    'category': tech_config['category'],
                    'detection_method': 'fallback'
                })
                self.stats['technologies_found'][tech_name] += 1
        
        return technologies
    
    async def detect_tags(self, page: Page) -> Dict:
        """Detect tracking tags"""
        try:
            scripts = await page.eval_on_selector_all(
                'script',
                'elements => elements.map(el => el.innerHTML + " " + (el.src || ""))'
            )
            
            page_content = ' '.join(scripts)
            page_url = page.url
            
            return self.detect_tags_comprehensive(page_content, page_url)
            
        except Exception as e:
            logging.error(f"Error detecting tags: {e}")
            return {}
    
    def parse_datalayer(self, datalayer: List[Dict]) -> Dict:
        """Parse and analyze dataLayer events"""
        parsed = {
            'total_events': len(datalayer),
            'events': [],
            'ga4_events': defaultdict(int),
            'ecommerce_events': [],
            'custom_events': []
        }
        
        for item in datalayer:
            if isinstance(item, dict):
                event_name = item.get('event', 'unknown')
                
                event_info = {
                    'event': event_name,
                    'data': item
                }
                
                if event_name in GA4_EVENTS:
                    parsed['ga4_events'][GA4_EVENTS[event_name]] += 1
                    event_info['type'] = 'ga4'
                    event_info['description'] = GA4_EVENTS[event_name]
                elif 'ecommerce' in item:
                    parsed['ecommerce_events'].append(event_info)
                    event_info['type'] = 'ecommerce'
                else:
                    parsed['custom_events'].append(event_name)
                    event_info['type'] = 'custom'
                
                parsed['events'].append(event_info)
        
        return parsed
    
    async def extract_datalayer(self, page: Page) -> Dict:
        """Extract and parse dataLayer"""
        try:
            datalayer_raw = await page.evaluate("""() => {
                if (typeof dataLayer !== 'undefined') {
                    return dataLayer;
                }
                if (typeof window.dataLayer !== 'undefined') {
                    return window.dataLayer;
                }
                return [];
            }""")
            
            if self.config['datalayer']['parse_events']:
                return self.parse_datalayer(datalayer_raw[:self.config['datalayer']['max_events']])
            else:
                return {'raw': datalayer_raw[:self.config['datalayer']['max_events']]}
                
        except Exception as e:
            logging.error(f"Error extracting dataLayer: {e}")
            return {}
    
    async def get_page_metadata(self, page: Page) -> Dict:
        """Extract comprehensive page metadata"""
        try:
            metadata = await page.evaluate("""() => {
                const getMeta = (name) => {
                    const el = document.querySelector(`meta[name="${name}"], meta[property="${name}"]`);
                    return el ? el.content : '';
                };
                
                return {
                    title: document.title,
                    description: getMeta('description'),
                    keywords: getMeta('keywords'),
                    canonical: document.querySelector('link[rel="canonical"]')?.href || '',
                    og_title: getMeta('og:title'),
                    og_description: getMeta('og:description'),
                    og_image: getMeta('og:image'),
                    h1: Array.from(document.querySelectorAll('h1')).map(h => h.textContent.trim()),
                    h2: Array.from(document.querySelectorAll('h2')).map(h => h.textContent.trim()).slice(0, 5),
                    robots: getMeta('robots'),
                    viewport: getMeta('viewport'),
                    charset: document.characterSet,
                    lang: document.documentElement.lang,
                    meta_tags: Array.from(document.querySelectorAll('meta')).map(m => ({
                        name: m.name || m.property,
                        content: m.content
                    }))
                };
            }""")
            return metadata
        except Exception as e:
            logging.error(f"Error extracting metadata: {e}")
            return {}
    
    async def get_performance_metrics(self, page: Page) -> Dict:
        """Capture page performance metrics"""
        try:
            metrics = await page.evaluate("""() => {
                const perfData = performance.getEntriesByType('navigation')[0];
                if (!perfData) return {};
                
                return {
                    load_time: perfData.loadEventEnd - perfData.fetchStart,
                    dom_content_loaded: perfData.domContentLoadedEventEnd - perfData.fetchStart,
                    first_paint: performance.getEntriesByType('paint')
                        .find(e => e.name === 'first-paint')?.startTime || 0,
                    first_contentful_paint: performance.getEntriesByType('paint')
                        .find(e => e.name === 'first-contentful-paint')?.startTime || 0,
                    transfer_size: perfData.transferSize,
                    dom_interactive: perfData.domInteractive - perfData.fetchStart
                };
            }""")
            return metrics
        except Exception as e:
            logging.error(f"Error capturing performance metrics: {e}")
            return {}
    
    def detect_technologies_wappalyzer(self, url: str) -> List[Dict]:
        """Use Wappalyzer CLI for technology detection"""
        if not self.config['technology']['use_wappalyzer']:
            return []
        
        try:
            result = subprocess.run(
                ['wappalyzer', url, '--pretty'],
                capture_output=True,
                text=True,
                timeout=self.config['technology']['wappalyzer_timeout']
            )
            
            if result.returncode == 0:
                try:
                    data = json.loads(result.stdout)
                    techs = data.get('technologies', [])
                    for tech in techs:
                        self.stats['technologies_found'][tech.get('name', 'Unknown')] += 1
                    return techs
                except json.JSONDecodeError:
                    logging.warning("Could not parse Wappalyzer output")
                    return []
            else:
                return []
                
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            logging.debug(f"Wappalyzer not available: {e}")
            return []
    
    async def crawl_page_with_retry(self, browser: Browser, url: str, depth: int) -> Optional[Dict]:
        """Crawl a page with retry logic"""
        retry_config = self.config['retry']
        
        for attempt in range(retry_config['max_retries'] + 1):
            try:
                result = await self.crawl_page(browser, url, depth)
                if result:
                    self.stats['pages_crawled'] += 1
                    return result
                else:
                    self.stats['pages_failed'] += 1
                    return None
                    
            except PlaywrightTimeout:
                if attempt < retry_config['max_retries']:
                    logging.warning(f"Timeout on {url}, retrying ({attempt + 1}/{retry_config['max_retries']})")
                    await asyncio.sleep(retry_config['retry_delay'])
                else:
                    logging.error(f"Failed after {retry_config['max_retries']} retries: {url}")
                    self.stats['pages_failed'] += 1
                    return None
                    
            except Exception as e:
                if attempt < retry_config['max_retries']:
                    logging.warning(f"Error on {url}: {e}, retrying ({attempt + 1}/{retry_config['max_retries']})")
                    await asyncio.sleep(retry_config['retry_delay'])
                else:
                    logging.error(f"Failed after {retry_config['max_retries']} retries: {url} - {e}")
                    self.stats['pages_failed'] += 1
                    return None
        
        return None
    
    async def crawl_page(self, browser: Browser, url: str, depth: int) -> Optional[Dict]:
        """Crawl a single page"""
        
        page = await browser.new_page(
            user_agent=self.config['browser']['user_agent'],
            viewport=self.config['browser']['viewport'],
            ignore_https_errors=self.config['browser']['ignore_https_errors']
        )
        
        network_logs = []
        
        async def log_request(request):
            tracking_domains = [
                'google-analytics.com', 'googletagmanager.com', 'facebook.com/tr',
                'analytics.tiktok.com', 'linkedin.com', 'ads-twitter.com',
                'hotjar.com', 'doubleclick.net', 'analytics.google.com',
                'omtrdc.net', 'demdex.net', 'tags.tiqcdn.com', 'cdn.segment.com'
            ]
            
            if any(domain in request.url for domain in tracking_domains):
                network_logs.append({
                    'url': request.url,
                    'method': request.method,
                    'type': request.resource_type,
                    'timestamp': datetime.now().isoformat()
                })
        
        page.on('request', log_request)
        
        try:
            response = await page.goto(
                url,
                wait_until='networkidle',
                timeout=self.timeout
            )
            
            if not response:
                await page.close()
                return None
            
            status = response.status
            
            if status >= 400:
                self.broken_links.append({
                    'url': url,
                    'status': status,
                    'depth': depth
                })
                await page.close()
                return None
            
            # Fix 15: Rate limit per page, not per batch
            await asyncio.sleep(self.rate_limit)
            
            metadata = await self.get_page_metadata(page)
            tags = await self.detect_tags(page)
            links, page_broken_links = await self.extract_links(page, url)
            self.broken_links.extend(page_broken_links)
            
            datalayer = {}
            if self.config['datalayer']['extract']:
                datalayer = await self.extract_datalayer(page)
            
            performance = {}
            if self.config['performance']['capture_metrics']:
                performance = await self.get_performance_metrics(page)
            
            screenshot_path = None
            if self.config['performance']['capture_screenshots']:
                # Fix 10: Use Path for cross-platform compatibility
                screenshot_dir = Path("screenshots")
                screenshot_dir.mkdir(exist_ok=True)
                safe_name = urlparse(url).path.replace('/', '_') or 'index'
                screenshot_path = str(screenshot_dir / f"{safe_name}.{self.config['performance']['screenshot_format']}")
                await page.screenshot(path=screenshot_path)
            
            html_content = await page.content()
            
            await page.close()
            
            technologies_wap = []
            technologies_fallback = []
            
            if self.config['technology']['use_wappalyzer']:
                technologies_wap = self.detect_technologies_wappalyzer(url)
            
            if self.config['technology']['use_fallback'] and not technologies_wap:
                technologies_fallback = self.detect_technologies_fallback(
                    html_content,
                    metadata.get('meta_tags', []),
                    {}
                )
            
            technologies = technologies_wap or technologies_fallback
            
            page_info = {
                'url': url,
                'depth': depth,
                'status': status,
                'metadata': metadata,
                'tags': tags,
                'datalayer': datalayer,
                'technologies': technologies,
                'performance': performance,
                'network_requests': network_logs,
                'internal_links_found': len(links),
                'screenshot': screenshot_path,
                'crawled_at': datetime.now().isoformat()
            }
            
            if depth < self.max_depth:
                for link in links:
                    if link not in self.visited_urls and link not in [u[0] for u in self.to_visit]:
                        self.to_visit.append((link, depth + 1))
            
            return page_info
            
        except Exception as e:
            logging.error(f"Error crawling {url}: {e}")
            await page.close()
            raise
    
    def display_progress(self):
        """Fix 11: Better progress indicator"""
        visited = len(self.visited_urls)
        success = self.stats['pages_crawled']
        failed = self.stats['pages_failed']
        remaining = len(self.to_visit)
        
        progress_bar = "=" * min(50, int(visited / self.max_pages * 50))
        percent = int(visited / self.max_pages * 100) if self.max_pages > 0 else 0
        
        print(f"\r[{progress_bar:<50}] {percent}% | "
              f"Visited: {visited}/{self.max_pages} | "
              f"Success: {success} | Failed: {failed} | Queue: {remaining}",
              end='', flush=True)
    
    async def crawl_concurrent(self):
        """Main crawl loop with concurrent page processing"""
        print(f"\n🚀 Starting crawl of {self.start_url}")
        print(f"⚙️  Settings: {self.max_pages} pages, depth {self.max_depth}, {self.concurrent_pages} concurrent")
        print(f"📊 Rate limit: {self.rate_limit}s per page\n")
        
        async with async_playwright() as p:
            browser = None
            try:
                browser = await p.chromium.launch(
                    headless=self.config['browser']['headless']
                )
                
                page_counter = 0
                
                while self.to_visit and len(self.visited_urls) < self.max_pages:
                    batch = []
                    for _ in range(self.concurrent_pages):
                        if self.to_visit and len(self.visited_urls) + len(batch) < self.max_pages:
                            url, depth = self.to_visit.pop(0)
                            if url not in self.visited_urls:
                                batch.append((url, depth))
                                self.visited_urls.add(url)
                    
                    if not batch:
                        break
                    
                    tasks = [self.crawl_page_with_retry(browser, url, depth) for url, depth in batch]
                    results = await asyncio.gather(*tasks, return_exceptions=True)
                    
                    for result in results:
                        if isinstance(result, dict):
                            self.page_data.append(result)
                            page_counter += 1
                            
                            # Fix 11: Update progress
                            self.display_progress()
                            
                            # Fix 9: Periodic flush to manage memory
                            if page_counter % self.memory_threshold == 0:
                                self.flush_to_disk()
                            
                            # Save progress periodically
                            if self.config['output']['save_progress'] and \
                               page_counter % self.config['output']['progress_interval'] == 0:
                                self.save_progress()
                
            finally:
                # Fix 14: Ensure browser closes
                if browser:
                    await browser.close()
        
        print("\n")  # New line after progress bar
        
        # Fix 9: Load any partial data
        self.load_partial_data()
        
        # Final save
        if self.config['output']['save_progress']:
            self.save_progress()
        
        print("=" * 80)
        print(f"✅ Crawl complete!")
        print(f"📄 Pages visited: {len(self.visited_urls)}")
        print(f"✅ Success: {self.stats['pages_crawled']}")
        print(f"❌ Failed: {self.stats['pages_failed']}")
        print(f"🔗 Broken links: {len(self.broken_links)}")
        print(f"🏷️  Unique tags: {len(self.stats['tags_found'])}")
        print(f"🛠️  Technologies: {len(self.stats['technologies_found'])}")
    
    def export_json(self, filename: str):
        """Export comprehensive JSON with all data"""
        output = {
            'crawl_info': {
                'start_url': self.start_url,
                'crawled_at': datetime.now().isoformat(),
                'total_pages': len(self.page_data),
                'pages_success': self.stats['pages_crawled'],
                'pages_failed': self.stats['pages_failed'],
                'broken_links': len(self.broken_links),
                'max_depth_reached': max([p['depth'] for p in self.page_data]) if self.page_data else 0,
                'tags_summary': dict(self.stats['tags_found']),
                'technologies_summary': dict(self.stats['technologies_found'])
            },
            'sitemap': [p['url'] for p in self.page_data],
            'broken_links': self.broken_links,
            'pages': self.page_data
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Exported JSON to {filename}")
    
    def export_csv(self, filename: str):
        """Export enhanced CSV with key metrics"""
        if not self.page_data:
            return
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            fieldnames = [
                'url', 'status', 'depth', 'title', 'description',
                'gtm', 'ga4', 'ua', 'facebook_pixel', 'linkedin', 'tiktok',
                'adobe_analytics', 'hotjar', 'segment', 'tags_total',
                'datalayer_events', 'ga4_events', 'ecommerce_events',
                'technologies', 'load_time_ms', 'internal_links'
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for page in self.page_data:
                tags = page.get('tags', {})
                
                row = {
                    'url': page['url'],
                    'status': page['status'],
                    'depth': page['depth'],
                    'title': page.get('metadata', {}).get('title', ''),
                    'description': page.get('metadata', {}).get('description', ''),
                    'gtm': 'Yes' if tags.get('google_tag_manager', {}).get('found') else 'No',
                    'ga4': 'Yes' if tags.get('google_analytics_4', {}).get('found') else 'No',
                    'ua': 'Yes' if tags.get('universal_analytics', {}).get('found') else 'No',
                    'facebook_pixel': 'Yes' if tags.get('facebook_pixel', {}).get('found') else 'No',
                    'linkedin': 'Yes' if tags.get('linkedin_insight', {}).get('found') else 'No',
                    'tiktok': 'Yes' if tags.get('tiktok_pixel', {}).get('found') else 'No',
                    'adobe_analytics': 'Yes' if tags.get('adobe_analytics', {}).get('found') else 'No',
                    'hotjar': 'Yes' if tags.get('hotjar', {}).get('found') else 'No',
                    'segment': 'Yes' if tags.get('segment', {}).get('found') else 'No',
                    'tags_total': len([t for t in tags.values() if t.get('found')]),
                    'datalayer_events': page.get('datalayer', {}).get('total_events', 0),
                    'ga4_events': len(page.get('datalayer', {}).get('ga4_events', {})),
                    'ecommerce_events': len(page.get('datalayer', {}).get('ecommerce_events', [])),
                    'technologies': len(page.get('technologies', [])),
                    'load_time_ms': int(page.get('performance', {}).get('load_time', 0)),
                    'internal_links': page.get('internal_links_found', 0)
                }
                writer.writerow(row)
        
        print(f"✓ Exported CSV to {filename}")
    
    def export_html(self, filename: str):
        """Export interactive HTML report"""
        tag_summary = defaultdict(int)
        for page in self.page_data:
            for tag_name, tag_data in page.get('tags', {}).items():
                if tag_data.get('found'):
                    tag_summary[tag_name] += 1
        
        tech_summary = defaultdict(int)
        for page in self.page_data:
            for tech in page.get('technologies', []):
                tech_summary[tech.get('name', 'Unknown')] += 1
        
        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Site Audit Report v2.1 - {self.base_domain}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif; 
               background: #f5f7fa; color: #2c3e50; line-height: 1.6; }}
        .container {{ max-width: 1400px; margin: 0 auto; padding: 20px; }}
        header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                 color: white; padding: 40px 20px; border-radius: 10px; margin-bottom: 30px; }}
        h1 {{ font-size: 2.5em; margin-bottom: 10px; }}
        .subtitle {{ opacity: 0.9; font-size: 1.1em; }}
        
        .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                      gap: 20px; margin: 30px 0; }}
        .stat-card {{ background: white; padding: 20px; border-radius: 8px;
                     box-shadow: 0 2px 8px rgba(0,0,0,0.1); text-align: center; }}
        .stat-number {{ font-size: 2.5em; font-weight: bold; color: #667eea; }}
        .stat-label {{ color: #7f8c8d; margin-top: 5px; }}
        
        .section {{ background: white; padding: 30px; border-radius: 8px;
                   box-shadow: 0 2px 8px rgba(0,0,0,0.1); margin: 20px 0; }}
        h2 {{ color: #2c3e50; border-bottom: 3px solid #667eea; padding-bottom: 10px; margin-bottom: 20px; }}
        
        .tag-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 15px; }}
        .tag-item {{ background: #f8f9fa; padding: 15px; border-radius: 5px; border-left: 4px solid #667eea; }}
        .tag-name {{ font-weight: 600; color: #2c3e50; margin-bottom: 5px; }}
        .tag-count {{ color: #7f8c8d; font-size: 0.9em; }}
        .tag-category {{ display: inline-block; background: #e3e8f7; padding: 2px 8px;
                        border-radius: 3px; font-size: 0.85em; margin-top: 5px; }}
        
        .page-list {{ margin-top: 20px; }}
        .page-item {{ background: #f8f9fa; padding: 15px; margin: 10px 0; border-radius: 5px;
                     border-left: 4px solid #3498db; }}
        .page-item:hover {{ background: #e8f4f8; }}
        .page-url {{ color: #2980b9; font-weight: 500; word-break: break-all; margin-bottom: 10px; }}
        .page-meta {{ display: flex; gap: 15px; flex-wrap: wrap; font-size: 0.9em; color: #7f8c8d; }}
        .badge {{ display: inline-block; padding: 3px 10px; border-radius: 12px;
                 font-size: 0.85em; font-weight: 500; }}
        .badge-success {{ background: #d4edda; color: #155724; }}
        .badge-warning {{ background: #fff3cd; color: #856404; }}
        .badge-info {{ background: #d1ecf1; color: #0c5460; }}
        .badge-danger {{ background: #f8d7da; color: #721c24; }}
        
        .tags-inline {{ display: flex; gap: 8px; flex-wrap: wrap; margin: 10px 0; }}
        .tag-badge {{ background: #667eea; color: white; padding: 4px 10px; border-radius: 4px; font-size: 0.85em; }}
        
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th {{ background: #667eea; color: white; padding: 12px; text-align: left; }}
        td {{ padding: 10px; border-bottom: 1px solid #ecf0f1; }}
        tr:hover {{ background: #f8f9fa; }}
        
        .broken-link {{ color: #e74c3c; }}
        
        .summary-box {{ background: #e8f5e9; border-left: 4px solid #4caf50; padding: 15px; margin: 15px 0; }}
        .warning-box {{ background: #fff3e0; border-left: 4px solid #ff9800; padding: 15px; margin: 15px 0; }}
        .version-badge {{ background: #667eea; color: white; padding: 5px 10px; border-radius: 5px; 
                         font-size: 0.9em; display: inline-block; margin-left: 10px; }}
        
        @media (max-width: 768px) {{
            .stats-grid {{ grid-template-columns: 1fr; }}
            .tag-grid {{ grid-template-columns: 1fr; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🔍 Site Audit Report <span class="version-badge">v2.1</span></h1>
            <div class="subtitle">{self.base_domain}</div>
            <div class="subtitle">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
        </header>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-number">{len(self.page_data)}</div>
                <div class="stat-label">Pages Crawled</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{len(tag_summary)}</div>
                <div class="stat-label">Unique Tags Found</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{len(tech_summary)}</div>
                <div class="stat-label">Technologies</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{len(self.broken_links)}</div>
                <div class="stat-label">Broken Links</div>
            </div>
        </div>
"""
        
        if tag_summary:
            html += """
        <div class="section">
            <h2>📊 Tags Detected</h2>
            <div class="tag-grid">
"""
            for tag_name, count in sorted(tag_summary.items(), key=lambda x: x[1], reverse=True):
                tag_config = TAG_PATTERNS.get(tag_name, {})
                category = tag_config.get('category', 'Other')
                display_name = tag_name.replace('_', ' ').title()
                html += f"""
                <div class="tag-item">
                    <div class="tag-name">{display_name}</div>
                    <div class="tag-count">Found on {count} page(s)</div>
                    <div class="tag-category">{category}</div>
                </div>
"""
            html += """
            </div>
        </div>
"""
        
        if tech_summary:
            html += """
        <div class="section">
            <h2>🛠️ Technologies Detected</h2>
            <div class="tag-grid">
"""
            for tech_name, count in sorted(tech_summary.items(), key=lambda x: x[1], reverse=True)[:20]:
                html += f"""
                <div class="tag-item">
                    <div class="tag-name">{tech_name}</div>
                    <div class="tag-count">Found on {count} page(s)</div>
                </div>
"""
            html += """
            </div>
        </div>
"""
        
        if self.broken_links:
            html += f"""
        <div class="section">
            <h2>⚠️ Broken Links</h2>
            <div class="warning-box">
                Found {len(self.broken_links)} broken links that should be fixed.
            </div>
            <table>
                <tr>
                    <th>URL</th>
                    <th>Status Code</th>
                    <th>Depth</th>
                </tr>
"""
            for link in self.broken_links[:50]:
                html += f"""
                <tr>
                    <td class="broken-link">{link['url']}</td>
                    <td>{link['status']}</td>
                    <td>{link['depth']}</td>
                </tr>
"""
            html += """
            </table>
        </div>
"""
        
        html += """
        <div class="section">
            <h2>📄 Page Details</h2>
            <div class="page-list">
"""
        
        for page in self.page_data[:100]:
            tags_found = [k.replace('_', ' ').title() for k, v in page.get('tags', {}).items() if v.get('found')]
            datalayer_info = page.get('datalayer', {})
            perf = page.get('performance', {})
            
            html += f"""
            <div class="page-item">
                <div class="page-url">{page.get('metadata', {}).get('title', 'No Title')} <br><small>{page['url']}</small></div>
                <div class="page-meta">
                    <span class="badge badge-success">Status: {page['status']}</span>
                    <span class="badge badge-info">Depth: {page['depth']}</span>
                    <span class="badge badge-info">Tags: {len(tags_found)}</span>
                    <span class="badge badge-info">DataLayer Events: {datalayer_info.get('total_events', 0)}</span>
"""
            if perf.get('load_time'):
                html += f"""
                    <span class="badge badge-warning">Load: {int(perf['load_time'])}ms</span>
"""
            html += """
                </div>
"""
            if tags_found:
                html += """
                <div class="tags-inline">
"""
                for tag in tags_found[:10]:
                    html += f"""
                    <span class="tag-badge">{tag}</span>
"""
                html += """
                </div>
"""
            html += """
            </div>
"""
        
        html += """
            </div>
        </div>
        
        <div class="section">
            <div class="summary-box">
                <strong>✅ Report Generated Successfully!</strong> 
                Check the JSON export for complete raw data including full dataLayer contents, 
                network requests, and detailed tag information.
            </div>
        </div>
        
    </div>
</body>
</html>
"""
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"✓ Exported HTML report to {filename}")


def load_config(config_file: Optional[str], cli_args: Dict) -> Dict:
    """Load and merge configuration from file and CLI arguments"""
    default_config_path = Path(script_dir) / 'config.yaml'
    
    # Fix 5: Better error handling for config loading
    config = None
    
    if config_file and Path(config_file).exists():
        if not YAML_AVAILABLE:
            print(f"⚠️  Cannot load {config_file}: PyYAML not installed")
            print("   Install with: pip install pyyaml")
            print("   Using default configuration...\n")
        else:
            try:
                with open(config_file, 'r') as f:
                    config = yaml.safe_load(f)
                print(f"✓ Loaded config from {config_file}\n")
            except yaml.YAMLError as e:
                print(f"❌ Error parsing config file {config_file}:")
                print(f"   {e}")
                print("   Using default configuration...\n")
            except Exception as e:
                print(f"⚠️  Could not read config file: {e}")
                print("   Using default configuration...\n")
    elif default_config_path.exists() and YAML_AVAILABLE:
        try:
            with open(default_config_path, 'r') as f:
                config = yaml.safe_load(f)
        except:
            pass
    
    # Use defaults if no config loaded
    if not config:
        config = {
            'crawl': {'max_pages': 100, 'max_depth': 3, 'rate_limit': 1.0, 'concurrent_pages': 3, 'timeout': 30},
            'retry': {'max_retries': 3, 'retry_delay': 2.0, 'retry_on_status': [500, 502, 503, 504, 429]},
            'browser': {'headless': True, 'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', 
                       'viewport': {'width': 1920, 'height': 1080}, 
                       'javascript_enabled': True, 'ignore_https_errors': False},
            'filters': {'respect_robots': True, 'exclude_patterns': [], 'include_patterns': [], 
                       'skip_extensions': ['.pdf', '.jpg', '.png', '.gif', '.css', '.js', '.zip']},
            'technology': {'use_wappalyzer': True, 'use_fallback': True, 'wappalyzer_timeout': 30},
            'tags': {'detect_all': True, 'custom_patterns': {}},
            'datalayer': {'extract': True, 'parse_events': True, 'max_events': 100},
            'performance': {'capture_metrics': True, 'capture_screenshots': False, 'screenshot_format': 'png'},
            'output': {'formats': ['json', 'csv', 'html'], 'prefix': 'site-audit', 'save_progress': True, 'progress_interval': 10},
            'logging': {'level': 'INFO', 'log_file': 'site-auditor.log', 'console': True},
            'resume': {'enabled': True, 'state_file': 'crawl_state.json'}
        }
    
    # Override with CLI arguments
    config['start_url'] = cli_args['url']
    if cli_args.get('max_pages'):
        config['crawl']['max_pages'] = cli_args['max_pages']
    if cli_args.get('max_depth'):
        config['crawl']['max_depth'] = cli_args['max_depth']
    if cli_args.get('rate_limit'):
        config['crawl']['rate_limit'] = cli_args['rate_limit']
    if cli_args.get('concurrent'):
        config['crawl']['concurrent_pages'] = cli_args['concurrent']
    if cli_args.get('output'):
        config['output']['prefix'] = cli_args['output']
    if cli_args.get('format'):
        if cli_args['format'] == 'all':
            config['output']['formats'] = ['json', 'csv', 'html']
        else:
            config['output']['formats'] = [cli_args['format']]
    if cli_args.get('exclude'):
        config['filters']['exclude_patterns'] = cli_args['exclude']
    if cli_args.get('include'):
        config['filters']['include_patterns'] = cli_args['include']
    if cli_args.get('no_resume'):
        config['resume']['enabled'] = False
    
    return config


async def main():
    # Fix 3: Check dependencies before starting
    print("🔍 Site Auditor v2.1 - Checking dependencies...\n")
    if not check_dependencies():
        print("\n❌ Please install missing dependencies and try again.")
        sys.exit(1)
    print("✓ All dependencies available\n")
    
    parser = argparse.ArgumentParser(
        description='Site Auditor v2.1 - Professional web crawler with comprehensive tag detection',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s https://example.com
  %(prog)s https://example.com --max-pages 500 --concurrent 5
  %(prog)s https://example.com --config my-config.yaml
  %(prog)s https://example.com --exclude "/admin.*" "/login.*"
        """
    )
    
    parser.add_argument('url', help='Starting URL to crawl')
    parser.add_argument('--config', help='Path to config file (YAML)')
    parser.add_argument('--max-pages', type=int, help='Maximum pages to crawl')
    parser.add_argument('--max-depth', type=int, help='Maximum crawl depth')
    parser.add_argument('--rate-limit', type=float, help='Seconds between requests')
    parser.add_argument('--concurrent', type=int, help='Concurrent pages (1-10)')
    parser.add_argument('--output', help='Output filename prefix')
    parser.add_argument('--format', choices=['json', 'csv', 'html', 'all'], help='Export format')
    parser.add_argument('--exclude', nargs='+', help='URL patterns to exclude (regex)')
    parser.add_argument('--include', nargs='+', help='URL patterns to include (regex)')
    parser.add_argument('--no-resume', action='store_true', help='Disable resume capability')
    
    args = parser.parse_args()
    
    config = load_config(args.config, vars(args))
    
    auditor = SiteAuditorV21(config)
    
    try:
        await auditor.crawl_concurrent()
        
        print("\n" + "=" * 80)
        print("📦 Exporting results...")
        print("=" * 80)
        
        output_prefix = config['output']['prefix']
        
        if 'json' in config['output']['formats']:
            auditor.export_json(f'{output_prefix}.json')
        
        if 'csv' in config['output']['formats']:
            auditor.export_csv(f'{output_prefix}.csv')
        
        if 'html' in config['output']['formats']:
            auditor.export_html(f'{output_prefix}.html')
        
        print("\n" + "=" * 80)
        print("🎉 Audit Complete!")
        print("=" * 80)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Crawl interrupted by user")
        if config['output']['save_progress']:
            auditor.save_progress()
            print(f"💾 Progress saved. Resume with same command.")
    except Exception as e:
        logging.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    asyncio.run(main())
