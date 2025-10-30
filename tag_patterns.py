"""
Tag Detection Patterns - Centralized configuration for all tracking tools
"""

TAG_PATTERNS = {
    # Google Products
    'google_tag_manager': {
        'patterns': [r'GTM-[A-Z0-9]{4,}'],
        'urls': ['googletagmanager.com/gtm.js', 'googletagmanager.com/ns.html'],
        'category': 'Tag Management'
    },
    'google_analytics_4': {
        'patterns': [r'G-[A-Z0-9]{10,}'],
        'urls': ['googletagmanager.com/gtag/js', 'google-analytics.com/g/collect'],
        'category': 'Analytics'
    },
    'universal_analytics': {
        'patterns': [r'UA-\d+-\d+'],
        'urls': ['google-analytics.com/analytics.js', 'google-analytics.com/ga.js'],
        'category': 'Analytics'
    },
    'google_ads': {
        'patterns': [r'AW-\d+'],
        'urls': ['googleadservices.com/pagead/conversion'],
        'category': 'Advertising'
    },
    'google_optimize': {
        'patterns': [r'GTM-[A-Z0-9]{4,}'],
        'urls': ['www.googleoptimize.com/optimize.js'],
        'category': 'A/B Testing'
    },
    
    # Meta/Facebook Products
    'facebook_pixel': {
        'patterns': [r'fbq\([\'"]init[\'"]\s*,\s*[\'"](\d+)[\'"]'],
        'urls': ['connect.facebook.net/en_US/fbevents.js'],
        'category': 'Advertising'
    },
    'facebook_capi': {
        'patterns': [r'facebook\.com/tr'],
        'urls': ['graph.facebook.com'],
        'category': 'Server-Side Tracking'
    },
    
    # LinkedIn
    'linkedin_insight': {
        'patterns': [r'_linkedin_partner_id\s*=\s*[\'"](\d+)[\'"]'],
        'urls': ['snap.licdn.com/li.lms-analytics', 'px.ads.linkedin.com'],
        'category': 'Advertising'
    },
    
    # TikTok
    'tiktok_pixel': {
        'patterns': [r'ttq\.load\([\'"]([A-Z0-9]+)[\'"]', r'tiktok_pixel_code[\'"]?\s*:\s*[\'"]([A-Z0-9]+)[\'"]'],
        'urls': ['analytics.tiktok.com/i18n/pixel/events.js'],
        'category': 'Advertising'
    },
    
    # Twitter/X
    'twitter_pixel': {
        'patterns': [r'twq\([\'"]init[\'"]'],
        'urls': ['static.ads-twitter.com/uwt.js'],
        'category': 'Advertising'
    },
    
    # Snapchat
    'snapchat_pixel': {
        'patterns': [r'snaptr\([\'"]init[\'"]'],
        'urls': ['sc-static.net/scevent.min.js'],
        'category': 'Advertising'
    },
    
    # Pinterest
    'pinterest_tag': {
        'patterns': [r'pintrk\([\'"]load[\'"]'],
        'urls': ['s.pinimg.com/ct/core.js'],
        'category': 'Advertising'
    },
    
    # Reddit
    'reddit_pixel': {
        'patterns': [r'rdt\([\'"]init[\'"]'],
        'urls': ['www.redditstatic.com/ads/pixel.js'],
        'category': 'Advertising'
    },
    
    # Adobe Products
    'adobe_analytics': {
        'patterns': [r's_account\s*=', r'var s=s_gi\('],
        'urls': ['omtrdc.net', 'adobedtm.com'],
        'category': 'Analytics'
    },
    'adobe_launch': {
        'patterns': [r'//assets\.adobedtm\.com/'],
        'urls': ['assets.adobedtm.com/launch'],
        'category': 'Tag Management'
    },
    'adobe_target': {
        'patterns': [r'adobe\.target'],
        'urls': ['tt.omtrdc.net'],
        'category': 'A/B Testing'
    },
    
    # Other Tag Managers
    'tealium': {
        'patterns': [r'utag\.js'],
        'urls': ['tags.tiqcdn.com'],
        'category': 'Tag Management'
    },
    'segment': {
        'patterns': [r'analytics\.load\([\'"]([a-zA-Z0-9]+)[\'"]'],
        'urls': ['cdn.segment.com/analytics.js'],
        'category': 'Customer Data Platform'
    },
    
    # Analytics Platforms
    'matomo': {
        'patterns': [r'_paq\.push', r'Matomo\.getTracker'],
        'urls': ['matomo.js', 'piwik.js'],
        'category': 'Analytics'
    },
    'mixpanel': {
        'patterns': [r'mixpanel\.init\([\'"]([a-zA-Z0-9]+)[\'"]'],
        'urls': ['cdn.mxpnl.com/libs/mixpanel'],
        'category': 'Analytics'
    },
    'heap': {
        'patterns': [r'heap\.load\([\'"](\d+)[\'"]'],
        'urls': ['cdn.heapanalytics.com'],
        'category': 'Analytics'
    },
    'amplitude': {
        'patterns': [r'amplitude\.getInstance\(\)\.init\([\'"]([a-zA-Z0-9]+)[\'"]'],
        'urls': ['cdn.amplitude.com'],
        'category': 'Analytics'
    },
    'kissmetrics': {
        'patterns': [r'_kmq\.push'],
        'urls': ['i.kissmetrics.com'],
        'category': 'Analytics'
    },
    'clicky': {
        'patterns': [r'clicky_site_ids\.push\((\d+)\)'],
        'urls': ['static.getclicky.com'],
        'category': 'Analytics'
    },
    
    # Heatmap & Session Recording
    'hotjar': {
        'patterns': [r'hjid:\s*(\d+)', r'hj\([\'"](hjid|identify)[\'"]'],
        'urls': ['static.hotjar.com'],
        'category': 'Heatmaps'
    },
    'crazy_egg': {
        'patterns': [r'crazyegg'],
        'urls': ['script.crazyegg.com'],
        'category': 'Heatmaps'
    },
    'mouseflow': {
        'patterns': [r'_mfq\.push'],
        'urls': ['cdn.mouseflow.com'],
        'category': 'Heatmaps'
    },
    'fullstory': {
        'patterns': [r'FS\.identify', r'window\[[\'"]\s*_fs_'],
        'urls': ['fullstory.com/s/fs.js'],
        'category': 'Session Recording'
    },
    'lucky_orange': {
        'patterns': [r'_loq\.push', r'LOQ_'],
        'urls': ['d10lpsik1i8c69.cloudfront.net'],
        'category': 'Heatmaps'
    },
    'clarity': {
        'patterns': [r'clarity\([\'"]set[\'"]'],
        'urls': ['clarity.ms'],
        'category': 'Heatmaps'
    },
    
    # A/B Testing
    'optimizely': {
        'patterns': [r'optimizely'],
        'urls': ['cdn.optimizely.com'],
        'category': 'A/B Testing'
    },
    'vwo': {
        'patterns': [r'_vwo_'],
        'urls': ['dev.visualwebsiteoptimizer.com'],
        'category': 'A/B Testing'
    },
    'ab_tasty': {
        'patterns': [r'ABTasty'],
        'urls': ['try.abtasty.com'],
        'category': 'A/B Testing'
    },
    
    # Consent Management
    'onetrust': {
        'patterns': [r'OneTrust', r'optanon'],
        'urls': ['cdn.cookielaw.org'],
        'category': 'Consent Management'
    },
    'cookiebot': {
        'patterns': [r'Cookiebot'],
        'urls': ['consent.cookiebot.com'],
        'category': 'Consent Management'
    },
    'trustarc': {
        'patterns': [r'truste', r'TrustArc'],
        'urls': ['consent.trustarc.com'],
        'category': 'Consent Management'
    },
    'quantcast': {
        'patterns': [r'quantserve\.com', r'__qca'],
        'urls': ['quantcast.mgr.consensu.org'],
        'category': 'Consent Management'
    },
    
    # E-commerce
    'shopify_analytics': {
        'patterns': [r'Shopify\.analytics'],
        'urls': ['cdn.shopify.com/s/javascripts/tricorder'],
        'category': 'E-commerce'
    },
    'criteo': {
        'patterns': [r'criteo'],
        'urls': ['static.criteo.net'],
        'category': 'Retargeting'
    },
    
    # Marketing Automation
    'hubspot': {
        'patterns': [r'_hsq\.push', r'portalId:\s*(\d+)'],
        'urls': ['js.hs-scripts.com', 'js.hubspot.com'],
        'category': 'Marketing Automation'
    },
    'marketo': {
        'patterns': [r'Munchkin\.init\([\'"]([0-9]+-[A-Z0-9-]+)[\'"]'],
        'urls': ['munchkin.marketo.net'],
        'category': 'Marketing Automation'
    },
    'pardot': {
        'patterns': [r'piTracker', r'pardot'],
        'urls': ['pi.pardot.com'],
        'category': 'Marketing Automation'
    },
    
    # Customer Support
    'intercom': {
        'patterns': [r'Intercom\([\'"]boot[\'"]', r'app_id:\s*[\'"]([a-z0-9]+)[\'"]'],
        'urls': ['widget.intercom.io'],
        'category': 'Customer Support'
    },
    'drift': {
        'patterns': [r'drift\.load\([\'"]([a-z0-9]+)[\'"]'],
        'urls': ['js.driftt.com'],
        'category': 'Customer Support'
    },
    'zendesk': {
        'patterns': [r'zE\(function\(\)'],
        'urls': ['static.zdassets.com'],
        'category': 'Customer Support'
    },
    
    # Other
    'microsoft_clarity': {
        'patterns': [r'clarity\([\'"]start[\'"]'],
        'urls': ['www.clarity.ms'],
        'category': 'Analytics'
    },
    'bing_ads': {
        'patterns': [r'UET_TAG_ID'],
        'urls': ['bat.bing.com'],
        'category': 'Advertising'
    },
    'yandex_metrica': {
        'patterns': [r'ym\(\d+'],
        'urls': ['mc.yandex.ru/metrika'],
        'category': 'Analytics'
    },
}

# Common GA4 events to identify in dataLayer
GA4_EVENTS = {
    'page_view': 'Page View',
    'scroll': 'Scroll Tracking',
    'click': 'Click Tracking',
    'view_item': 'Product View',
    'add_to_cart': 'Add to Cart',
    'remove_from_cart': 'Remove from Cart',
    'view_cart': 'View Cart',
    'begin_checkout': 'Begin Checkout',
    'add_payment_info': 'Payment Info Added',
    'add_shipping_info': 'Shipping Info Added',
    'purchase': 'Purchase',
    'refund': 'Refund',
    'view_item_list': 'Product List View',
    'select_item': 'Product Click',
    'view_promotion': 'Promotion View',
    'select_promotion': 'Promotion Click',
    'login': 'Login',
    'sign_up': 'Sign Up',
    'share': 'Share',
    'search': 'Search',
    'generate_lead': 'Lead Generation',
    'view_search_results': 'Search Results View',
    'file_download': 'File Download',
    'form_start': 'Form Start',
    'form_submit': 'Form Submit'
}

# Technology fallback patterns (when Wappalyzer unavailable)
TECHNOLOGY_PATTERNS = {
    'wordpress': {
        'patterns': [r'wp-content/', r'wp-includes/', r'/wordpress/'],
        'meta': [('generator', r'WordPress')],
        'category': 'CMS'
    },
    'shopify': {
        'patterns': [r'cdn\.shopify\.com', r'Shopify\.theme'],
        'meta': [],
        'category': 'E-commerce'
    },
    'react': {
        'patterns': [r'react\.', r'React\.createElement', r'__REACT'],
        'meta': [],
        'category': 'JavaScript Framework'
    },
    'vue': {
        'patterns': [r'Vue\.js', r'vue\.', r'__VUE__'],
        'meta': [],
        'category': 'JavaScript Framework'
    },
    'angular': {
        'patterns': [r'angular\.', r'ng-app', r'ng-controller'],
        'meta': [],
        'category': 'JavaScript Framework'
    },
    'next_js': {
        'patterns': [r'__NEXT_DATA__', r'_next/static'],
        'meta': [],
        'category': 'JavaScript Framework'
    },
    'jquery': {
        'patterns': [r'jquery', r'jQuery'],
        'meta': [],
        'category': 'JavaScript Library'
    },
    'bootstrap': {
        'patterns': [r'bootstrap'],
        'meta': [],
        'category': 'CSS Framework'
    },
    'cloudflare': {
        'patterns': [r'cloudflare'],
        'headers': [('server', r'cloudflare')],
        'category': 'CDN'
    },
}
