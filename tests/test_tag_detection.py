"""Tests for marketing/analytics tag detection."""

import pytest


class TestGoogleTags:
    def test_gtm_container_id(self, auditor):
        content = '<script src="https://www.googletagmanager.com/gtm.js?id=GTM-ABCD1234"></script>'
        result = auditor.detect_tags(content, 'https://example.com')
        assert 'google_tag_manager' in result
        assert result['google_tag_manager']['found'] is True
        assert 'GTM-ABCD1234' in result['google_tag_manager']['ids']

    def test_ga4_measurement_id(self, auditor):
        content = 'gtag("config", "G-ABC1234567");'
        result = auditor.detect_tags(content, 'https://example.com')
        assert 'google_analytics_4' in result
        assert 'G-ABC1234567' in result['google_analytics_4']['ids']

    def test_ga4_via_url(self, auditor):
        content = '<script src="https://www.googletagmanager.com/gtag/js?id=G-XYZ"></script>'
        result = auditor.detect_tags(content, 'https://example.com')
        assert 'google_analytics_4' in result

    def test_universal_analytics(self, auditor):
        content = 'ga("create", "UA-12345-1", "auto");'
        result = auditor.detect_tags(content, 'https://example.com')
        assert 'universal_analytics' in result
        assert 'UA-12345-1' in result['universal_analytics']['ids']

    def test_google_ads(self, auditor):
        content = 'gtag("config", "AW-123456789");'
        result = auditor.detect_tags(content, 'https://example.com')
        assert 'google_ads' in result
        assert 'AW-123456789' in result['google_ads']['ids']

    def test_google_optimize_url(self, auditor):
        content = '<script src="https://www.googleoptimize.com/optimize.js?id=OPT-12345"></script>'
        result = auditor.detect_tags(content, 'https://example.com')
        assert 'google_optimize' in result


class TestMetaTags:
    def test_facebook_pixel(self, auditor):
        content = "fbq('init', '1234567890');"
        result = auditor.detect_tags(content, 'https://example.com')
        assert 'facebook_pixel' in result
        assert '1234567890' in result['facebook_pixel']['ids']

    def test_facebook_pixel_via_url(self, auditor):
        content = '<script src="https://connect.facebook.net/en_US/fbevents.js"></script>'
        result = auditor.detect_tags(content, 'https://example.com')
        assert 'facebook_pixel' in result


class TestSocialPixels:
    def test_linkedin_insight(self, auditor):
        content = '_linkedin_partner_id = "12345";'
        result = auditor.detect_tags(content, 'https://example.com')
        assert 'linkedin_insight' in result
        assert '12345' in result['linkedin_insight']['ids']

    def test_tiktok_pixel(self, auditor):
        content = "ttq.load('ABC123DEF');"
        result = auditor.detect_tags(content, 'https://example.com')
        assert 'tiktok_pixel' in result
        assert 'ABC123DEF' in result['tiktok_pixel']['ids']

    def test_twitter_pixel(self, auditor):
        content = "twq('init', 'abc123');"
        result = auditor.detect_tags(content, 'https://example.com')
        assert 'twitter_pixel' in result

    def test_snapchat_pixel(self, auditor):
        content = "snaptr('init', 'abc-123');"
        result = auditor.detect_tags(content, 'https://example.com')
        assert 'snapchat_pixel' in result

    def test_pinterest_tag(self, auditor):
        content = "pintrk('load', '1234');"
        result = auditor.detect_tags(content, 'https://example.com')
        assert 'pinterest_tag' in result

    def test_reddit_pixel(self, auditor):
        content = "rdt('init', 'abc');"
        result = auditor.detect_tags(content, 'https://example.com')
        assert 'reddit_pixel' in result


class TestAnalyticsPlatforms:
    def test_hotjar(self, auditor):
        content = '<script>hj("identify", "user123");</script> https://static.hotjar.com/c/hotjar.js'
        result = auditor.detect_tags(content, 'https://example.com')
        assert 'hotjar' in result

    def test_mixpanel(self, auditor):
        content = "mixpanel.init('abc123def');"
        result = auditor.detect_tags(content, 'https://example.com')
        assert 'mixpanel' in result

    def test_segment(self, auditor):
        content = "analytics.load('writekey123');"
        result = auditor.detect_tags(content, 'https://example.com')
        assert 'segment' in result

    def test_amplitude(self, auditor):
        content = "amplitude.getInstance().init('apikey123');"
        result = auditor.detect_tags(content, 'https://example.com')
        assert 'amplitude' in result

    def test_heap(self, auditor):
        content = "heap.load('9876543210');"
        result = auditor.detect_tags(content, 'https://example.com')
        assert 'heap' in result
        assert '9876543210' in result['heap']['ids']


class TestMarketingAutomation:
    def test_hubspot(self, auditor):
        content = "_hsq.push(['identify', {}]);"
        result = auditor.detect_tags(content, 'https://example.com')
        assert 'hubspot' in result

    def test_marketo(self, auditor):
        content = "Munchkin.init('123-ABC-456');"
        result = auditor.detect_tags(content, 'https://example.com')
        assert 'marketo' in result
        assert '123-ABC-456' in result['marketo']['ids']

    def test_pardot(self, auditor):
        content = '<script src="https://pi.pardot.com/pd.js"></script>'
        result = auditor.detect_tags(content, 'https://example.com')
        assert 'pardot' in result

    def test_pardot_via_go_url(self, auditor):
        content = '<iframe src="https://go.pardot.com/l/123/form"></iframe>'
        result = auditor.detect_tags(content, 'https://example.com')
        assert 'pardot' in result

    def test_salesforce_marketing_cloud(self, auditor):
        content = "_etmc.push(['trackPageView']);"
        result = auditor.detect_tags(content, 'https://example.com')
        assert 'salesforce_marketing_cloud' in result

    def test_dynamics_365_marketing(self, auditor):
        content = '<script>var msdynmkt = { trackingId: "abc123" };</script>'
        result = auditor.detect_tags(content, 'https://example.com')
        assert 'dynamics_365_marketing' in result

    def test_eloqua(self, auditor):
        content = '<script>var elqTrackId = "1234";</script>'
        result = auditor.detect_tags(content, 'https://example.com')
        assert 'eloqua' in result

    def test_eloqua_via_url(self, auditor):
        content = '<script src="https://t.eloqua.com/visitor/v200/svrGP.aspx"></script>'
        result = auditor.detect_tags(content, 'https://example.com')
        assert 'eloqua' in result

    def test_activecampaign(self, auditor):
        content = 'var trackcmp_email = ""; var actid = "123456789";'
        result = auditor.detect_tags(content, 'https://example.com')
        assert 'activecampaign' in result

    def test_activecampaign_via_url(self, auditor):
        content = '<script src="https://trackcmp.net/visit?actid=123"></script>'
        result = auditor.detect_tags(content, 'https://example.com')
        assert 'activecampaign' in result

    def test_klaviyo(self, auditor):
        content = "_learnq.push(['identify', {email: 'test@test.com'}]);"
        result = auditor.detect_tags(content, 'https://example.com')
        assert 'klaviyo' in result

    def test_klaviyo_via_url(self, auditor):
        content = '<script src="https://static.klaviyo.com/onsite/js/klaviyo.js"></script>'
        result = auditor.detect_tags(content, 'https://example.com')
        assert 'klaviyo' in result

    def test_mailchimp(self, auditor):
        content = '<form action="https://example.us1.list-manage.com/subscribe/post">'
        result = auditor.detect_tags(content, 'https://example.com')
        assert 'mailchimp' in result

    def test_braze(self, auditor):
        content = 'braze.initialize("api-key", {baseUrl: "sdk.iad-01.braze.com"});'
        result = auditor.detect_tags(content, 'https://example.com')
        assert 'braze' in result

    def test_braze_legacy_appboy(self, auditor):
        content = '<script src="https://js.appboycdn.com/web-sdk/4.0/braze.min.js"></script>'
        result = auditor.detect_tags(content, 'https://example.com')
        assert 'braze' in result

    def test_customer_io(self, auditor):
        content = '<script src="https://assets.customer.io/assets/track.js"></script>'
        result = auditor.detect_tags(content, 'https://example.com')
        assert 'customer_io' in result

    def test_iterable(self, auditor):
        content = '<script src="https://js.iterable.com/analytics.js"></script>'
        result = auditor.detect_tags(content, 'https://example.com')
        assert 'iterable' in result

    def test_sendgrid(self, auditor):
        content = '<script src="https://mc.sendgrid.com/js/track.js"></script>'
        result = auditor.detect_tags(content, 'https://example.com')
        assert 'sendgrid' in result


class TestCustomerSupport:
    def test_freshdesk(self, auditor):
        content = '<script>window.FreshworksWidget("open");</script>'
        result = auditor.detect_tags(content, 'https://example.com')
        assert 'freshdesk' in result

    def test_livechat(self, auditor):
        content = '<script>window.__lc.license = 12345678;</script>'
        result = auditor.detect_tags(content, 'https://example.com')
        assert 'livechat' in result

    def test_hubspot_conversations(self, auditor):
        content = '<script src="https://js.usemessages.com/conversations-embed.js"></script>'
        result = auditor.detect_tags(content, 'https://example.com')
        assert 'hubspot_conversations' in result


class TestCRM:
    def test_salesforce_web_to_lead(self, auditor):
        content = '<input type="hidden" name="oid" value="00D5e000000abcd">'
        result = auditor.detect_tags(content, 'https://example.com')
        assert 'salesforce_web_to_lead' in result


class TestEcommerceTracking:
    def test_shopify_web_pixels(self, auditor):
        content = '<script src="https://cdn.shopify.com/shopifycloud/web-pixels-manager/v2/pixel.js"></script>'
        result = auditor.detect_tags(content, 'https://example.com')
        assert 'shopify_web_pixels' in result

    def test_shopify_web_pixels_via_pattern(self, auditor):
        content = 'Shopify.analytics.publish("page_viewed", {});'
        result = auditor.detect_tags(content, 'https://example.com')
        assert 'shopify_web_pixels' in result

    def test_attentive(self, auditor):
        content = '<script src="https://cdn.attn.tv/tag.js"></script>'
        result = auditor.detect_tags(content, 'https://example.com')
        assert 'attentive' in result

    def test_attentive_via_pattern(self, auditor):
        content = 'var __attentive_domain = "example.attn.tv";'
        result = auditor.detect_tags(content, 'https://example.com')
        assert 'attentive' in result

    def test_yotpo(self, auditor):
        content = '<div data-yotpo-product-id="123456"></div>'
        result = auditor.detect_tags(content, 'https://example.com')
        assert 'yotpo' in result

    def test_yotpo_via_url(self, auditor):
        content = '<script src="https://staticw2.yotpo.com/widget.js"></script>'
        result = auditor.detect_tags(content, 'https://example.com')
        assert 'yotpo' in result

    def test_nosto(self, auditor):
        content = '<script src="https://connect.nosto.com/include/abc123"></script>'
        result = auditor.detect_tags(content, 'https://example.com')
        assert 'nosto' in result

    def test_smile_io(self, auditor):
        content = '<script src="https://cdn.smile.io/v1/smile.js"></script>'
        result = auditor.detect_tags(content, 'https://example.com')
        assert 'smile_io' in result

    def test_rebuy(self, auditor):
        content = '<script src="https://cdn.rebuyengine.com/onsite/js/rebuy.js"></script>'
        result = auditor.detect_tags(content, 'https://example.com')
        assert 'rebuy' in result

    def test_privy(self, auditor):
        content = '<script src="https://widget.privy.com/assets/widget.js"></script>'
        result = auditor.detect_tags(content, 'https://example.com')
        assert 'privy' in result

    def test_gorgias(self, auditor):
        content = '<script src="https://config.gorgias.chat/bundle-loader/abc123"></script>'
        result = auditor.detect_tags(content, 'https://example.com')
        assert 'gorgias' in result

    def test_gorgias_via_pattern(self, auditor):
        content = '<div id="gorgias-chat-widget"></div>'
        result = auditor.detect_tags(content, 'https://example.com')
        assert 'gorgias' in result

    def test_aftership(self, auditor):
        content = '<script src="https://cdn.aftership.com/sdk/aftership-tracking.js"></script>'
        result = auditor.detect_tags(content, 'https://example.com')
        assert 'aftership' in result

    def test_recharge(self, auditor):
        content = '<script src="https://static.rechargecdn.com/assets/js/widget.js"></script>'
        result = auditor.detect_tags(content, 'https://example.com')
        assert 'recharge' in result

    def test_bold_commerce(self, auditor):
        content = '<script src="https://cdn.boldcommerce.com/bold/js/cashier.js"></script>'
        result = auditor.detect_tags(content, 'https://example.com')
        assert 'bold_commerce' in result


class TestConsentManagement:
    def test_onetrust(self, auditor):
        content = '<script src="https://cdn.cookielaw.org/scripttemplates/otSDKStub.js"></script>'
        result = auditor.detect_tags(content, 'https://example.com')
        assert 'onetrust' in result

    def test_cookiebot(self, auditor):
        content = '<script src="https://consent.cookiebot.com/uc.js"></script>'
        result = auditor.detect_tags(content, 'https://example.com')
        assert 'cookiebot' in result


class TestNoFalsePositives:
    def test_empty_content(self, auditor):
        result = auditor.detect_tags('', 'https://example.com')
        assert result == {}

    def test_plain_html(self, auditor):
        content = '<html><head><title>Hello</title></head><body><p>World</p></body></html>'
        result = auditor.detect_tags(content, 'https://example.com')
        assert result == {}

    def test_stats_updated(self, auditor):
        content = "fbq('init', '999');"
        auditor.detect_tags(content, 'https://example.com')
        assert auditor.stats['tags_found']['facebook_pixel'] == 1

    def test_category_field(self, auditor):
        content = '<script src="https://static.hotjar.com/c/hotjar.js"></script>'
        result = auditor.detect_tags(content, 'https://example.com')
        assert result['hotjar']['category'] == 'Heatmaps'
