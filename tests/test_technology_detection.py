"""Tests for technology detection patterns."""

import pytest


class TestCMSDetection:
    def test_wordpress_via_html(self, auditor):
        content = '<link rel="stylesheet" href="/wp-content/themes/theme/style.css">'
        result = auditor.detect_technologies(content, [], {})
        names = [t['name'] for t in result]
        assert 'wordpress' in names

    def test_wordpress_via_meta(self, auditor):
        meta = [{'name': 'generator', 'content': 'WordPress 6.4'}]
        result = auditor.detect_technologies('', meta, {})
        names = [t['name'] for t in result]
        assert 'wordpress' in names

    def test_drupal(self, auditor):
        content = '<script>Drupal.settings = {};</script>'
        result = auditor.detect_technologies(content, [], {})
        names = [t['name'] for t in result]
        assert 'drupal' in names

    def test_wix(self, auditor):
        meta = [{'name': 'generator', 'content': 'Wix.com Website Builder'}]
        result = auditor.detect_technologies('', meta, {})
        names = [t['name'] for t in result]
        assert 'wix' in names

    def test_squarespace(self, auditor):
        content = '<script src="https://static1.squarespace.com/universal/scripts.js"></script>'
        result = auditor.detect_technologies(content, [], {})
        names = [t['name'] for t in result]
        assert 'squarespace' in names

    def test_webflow(self, auditor):
        content = '<html data-wf-site="abc123">'
        result = auditor.detect_technologies(content, [], {})
        names = [t['name'] for t in result]
        assert 'webflow' in names

    def test_ghost(self, auditor):
        meta = [{'name': 'generator', 'content': 'Ghost 5.0'}]
        result = auditor.detect_technologies('', meta, {})
        names = [t['name'] for t in result]
        assert 'ghost' in names


class TestEcommerceDetection:
    def test_shopify(self, auditor):
        content = '<script src="https://cdn.shopify.com/s/files/theme.js"></script>'
        result = auditor.detect_technologies(content, [], {})
        names = [t['name'] for t in result]
        assert 'shopify' in names

    def test_woocommerce_via_meta(self, auditor):
        meta = [{'name': 'generator', 'content': 'WooCommerce 8.0'}]
        result = auditor.detect_technologies('', meta, {})
        names = [t['name'] for t in result]
        assert 'woocommerce' in names

    def test_magento(self, auditor):
        content = '<script>require(["mage/cookies"]);</script>'
        result = auditor.detect_technologies(content, [], {})
        names = [t['name'] for t in result]
        assert 'magento' in names

    def test_stripe(self, auditor):
        content = '<script src="https://js.stripe.com/v3/"></script>'
        result = auditor.detect_technologies(content, [], {})
        names = [t['name'] for t in result]
        assert 'stripe' in names


class TestFrameworkDetection:
    def test_react(self, auditor):
        content = '<div id="root" data-reactroot></div><script>React.createElement</script>'
        result = auditor.detect_technologies(content, [], {})
        names = [t['name'] for t in result]
        assert 'react' in names

    def test_vue(self, auditor):
        content = '<div data-v-a1b2c3d4></div>'
        result = auditor.detect_technologies(content, [], {})
        names = [t['name'] for t in result]
        assert 'vue' in names

    def test_angular(self, auditor):
        content = '<app-root ng-version="17.0.0"></app-root>'
        result = auditor.detect_technologies(content, [], {})
        names = [t['name'] for t in result]
        assert 'angular' in names

    def test_next_js(self, auditor):
        content = '<script id="__NEXT_DATA__" type="application/json">{}</script>'
        result = auditor.detect_technologies(content, [], {})
        names = [t['name'] for t in result]
        assert 'next_js' in names

    def test_nuxt(self, auditor):
        content = '<script>window.__NUXT__={}</script>'
        result = auditor.detect_technologies(content, [], {})
        names = [t['name'] for t in result]
        assert 'nuxt' in names

    def test_gatsby(self, auditor):
        content = '<div id="___gatsby"></div>'
        result = auditor.detect_technologies(content, [], {})
        names = [t['name'] for t in result]
        assert 'gatsby' in names

    def test_svelte(self, auditor):
        content = '<div class="svelte-abc123"></div>'
        result = auditor.detect_technologies(content, [], {})
        names = [t['name'] for t in result]
        assert 'svelte' in names

    def test_astro(self, auditor):
        content = '<astro-island></astro-island>'
        result = auditor.detect_technologies(content, [], {})
        names = [t['name'] for t in result]
        assert 'astro' in names


class TestHeaderDetection:
    def test_nginx(self, auditor):
        result = auditor.detect_technologies('', [], {'server': 'nginx/1.24.0'})
        names = [t['name'] for t in result]
        assert 'nginx' in names

    def test_apache(self, auditor):
        result = auditor.detect_technologies('', [], {'server': 'Apache/2.4.57'})
        names = [t['name'] for t in result]
        assert 'apache' in names

    def test_cloudflare(self, auditor):
        result = auditor.detect_technologies('', [], {'server': 'cloudflare'})
        names = [t['name'] for t in result]
        assert 'cloudflare' in names

    def test_vercel(self, auditor):
        result = auditor.detect_technologies('', [], {'x-vercel-id': 'iad1::abc123'})
        names = [t['name'] for t in result]
        assert 'vercel' in names

    def test_netlify(self, auditor):
        result = auditor.detect_technologies('', [], {'server': 'Netlify'})
        names = [t['name'] for t in result]
        assert 'netlify' in names

    def test_php(self, auditor):
        result = auditor.detect_technologies('', [], {'x-powered-by': 'PHP/8.2.0'})
        names = [t['name'] for t in result]
        assert 'php' in names

    def test_asp_net_via_header(self, auditor):
        result = auditor.detect_technologies('', [], {'x-powered-by': 'ASP.NET'})
        names = [t['name'] for t in result]
        assert 'asp_net' in names

    def test_asp_net_via_viewstate(self, auditor):
        content = '<input type="hidden" name="__VIEWSTATE" value="abc123" />'
        result = auditor.detect_technologies(content, [], {})
        names = [t['name'] for t in result]
        assert 'asp_net' in names


class TestMiscDetection:
    def test_google_fonts(self, auditor):
        content = '<link href="https://fonts.googleapis.com/css2?family=Roboto" rel="stylesheet">'
        result = auditor.detect_technologies(content, [], {})
        names = [t['name'] for t in result]
        assert 'google_fonts' in names

    def test_recaptcha(self, auditor):
        content = '<script src="https://www.google.com/recaptcha/api.js"></script>'
        result = auditor.detect_technologies(content, [], {})
        names = [t['name'] for t in result]
        assert 'recaptcha' in names

    def test_sentry(self, auditor):
        content = '<script>Sentry.init({dsn: "https://abc@sentry.io/123"});</script>'
        result = auditor.detect_technologies(content, [], {})
        names = [t['name'] for t in result]
        assert 'sentry' in names

    def test_tailwindcss(self, auditor):
        content = '<link href="/css/tailwindcss.min.css" rel="stylesheet">'
        result = auditor.detect_technologies(content, [], {})
        names = [t['name'] for t in result]
        assert 'tailwindcss' in names

    def test_category_field(self, auditor):
        content = '<script src="https://cdn.shopify.com/s/files/theme.js"></script>'
        result = auditor.detect_technologies(content, [], {})
        shopify = [t for t in result if t['name'] == 'shopify'][0]
        assert shopify['category'] == 'E-commerce'

    def test_empty_content_no_matches(self, auditor):
        result = auditor.detect_technologies('', [], {})
        assert result == []

    def test_stats_updated(self, auditor):
        content = '<div id="___gatsby"></div>'
        auditor.detect_technologies(content, [], {})
        assert auditor.stats['technologies_found']['gatsby'] == 1


class TestFalsePositiveHardening:
    def test_magento_not_detected_from_text_mention(self, auditor):
        content = '<html><body><p>Compare Magento vs Shopify for your store</p></body></html>'
        result = auditor.detect_technologies(content, [], {})
        names = [t['name'] for t in result]
        assert 'magento' not in names

    def test_magento_detected_from_specific_pattern(self, auditor):
        content = '<script>require(["mage/cookies"]);</script>'
        result = auditor.detect_technologies(content, [], {})
        names = [t['name'] for t in result]
        assert 'magento' in names

    def test_woocommerce_not_detected_from_text_mention(self, auditor):
        content = '<html><body><p>WooCommerce is a popular e-commerce platform</p></body></html>'
        result = auditor.detect_technologies(content, [], {})
        names = [t['name'] for t in result]
        assert 'woocommerce' not in names

    def test_woocommerce_detected_from_plugin_path(self, auditor):
        content = '<link rel="stylesheet" href="/wp-content/plugins/woocommerce/assets/css/style.css">'
        result = auditor.detect_technologies(content, [], {})
        names = [t['name'] for t in result]
        assert 'woocommerce' in names

    def test_woocommerce_detected_from_class(self, auditor):
        content = '<div class="woocommerce product-list"></div>'
        result = auditor.detect_technologies(content, [], {})
        names = [t['name'] for t in result]
        assert 'woocommerce' in names

    def test_bootstrap_not_detected_from_common_classes(self, auditor):
        content = '<div class="container row col-md-6"><p>Hello</p></div>'
        result = auditor.detect_technologies(content, [], {})
        names = [t['name'] for t in result]
        assert 'bootstrap' not in names

    def test_bootstrap_detected_from_filename(self, auditor):
        content = '<script src="/js/bootstrap.5.3.min.js"></script>'
        result = auditor.detect_technologies(content, [], {})
        names = [t['name'] for t in result]
        assert 'bootstrap' in names

    def test_tailwind_not_detected_from_utility_classes(self, auditor):
        content = '<div class="flex grid text-sm bg-gray-100"><p>Hello</p></div>'
        result = auditor.detect_technologies(content, [], {})
        names = [t['name'] for t in result]
        assert 'tailwindcss' not in names

    def test_tailwind_detected_from_filename(self, auditor):
        content = '<link href="/css/tailwindcss.min.css" rel="stylesheet">'
        result = auditor.detect_technologies(content, [], {})
        names = [t['name'] for t in result]
        assert 'tailwindcss' in names


class TestEvidenceModel:
    def test_evidence_field_present(self, auditor):
        content = '<script src="https://cdn.shopify.com/s/files/theme.js"></script>'
        result = auditor.detect_technologies(content, [], {})
        shopify = [t for t in result if t['name'] == 'shopify'][0]
        assert 'evidence' in shopify
        assert isinstance(shopify['evidence'], list)
        assert len(shopify['evidence']) > 0

    def test_confidence_high_from_network_request(self, auditor):
        requests = [
            {'url': 'https://cdn.shopify.com/s/files/theme.js',
             'method': 'GET', 'type': 'script', 'post_data': None},
        ]
        result = auditor.detect_technologies('', [], {}, network_requests=requests)
        shopify = [t for t in result if t['name'] == 'shopify']
        assert len(shopify) == 1
        assert shopify[0]['confidence'] == 'high'

    def test_confidence_high_from_header(self, auditor):
        result = auditor.detect_technologies('', [], {'server': 'cloudflare'})
        cf = [t for t in result if t['name'] == 'cloudflare'][0]
        assert cf['confidence'] == 'high'
        assert any('header:' in e for e in cf['evidence'])

    def test_confidence_medium_from_js_pattern(self, auditor):
        content = '<script>React.createElement("div")</script>'
        result = auditor.detect_technologies(content, [], {})
        react = [t for t in result if t['name'] == 'react'][0]
        assert react['confidence'] == 'medium'
        assert any('html_pattern:' in e for e in react['evidence'])

    def test_confidence_from_meta_tag(self, auditor):
        meta = [{'name': 'generator', 'content': 'WordPress 6.4'}]
        result = auditor.detect_technologies('', meta, {})
        wp = [t for t in result if t['name'] == 'wordpress'][0]
        assert wp['confidence'] == 'high'
        assert any('meta:' in e for e in wp['evidence'])


class TestNetworkCorroboration:
    def test_technology_detected_from_network_request(self, auditor):
        requests = [
            {'url': 'https://cdn.shopify.com/s/files/1/theme.js',
             'method': 'GET', 'type': 'script', 'post_data': None},
        ]
        result = auditor.detect_technologies('', [], {}, network_requests=requests)
        names = [t['name'] for t in result]
        assert 'shopify' in names

    def test_technology_gains_higher_confidence_with_network(self, auditor):
        content = '<script src="https://cdn.shopify.com/s/files/theme.js"></script>'
        requests = [
            {'url': 'https://cdn.shopify.com/s/files/theme.js',
             'method': 'GET', 'type': 'script', 'post_data': None},
        ]
        result = auditor.detect_technologies(content, [], {}, network_requests=requests)
        shopify = [t for t in result if t['name'] == 'shopify'][0]
        assert shopify['confidence'] == 'high'
        assert any('html_pattern:' in e for e in shopify['evidence'])
        assert any('request_host:' in e for e in shopify['evidence'])
