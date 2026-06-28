"""Tests for dataLayer parsing."""

import pytest


class TestDataLayerParsing:
    def test_empty_datalayer(self, auditor):
        result = auditor._parse_datalayer([])
        assert result['total_events'] == 0
        assert result['events'] == []

    def test_ga4_page_view(self, auditor):
        datalayer = [{'event': 'page_view', 'page_title': 'Home'}]
        result = auditor._parse_datalayer(datalayer)
        assert result['total_events'] == 1
        assert result['ga4_events']['Page View'] == 1
        assert result['events'][0]['type'] == 'ga4'

    def test_ga4_purchase(self, auditor):
        datalayer = [{'event': 'purchase', 'value': 99.99, 'currency': 'USD'}]
        result = auditor._parse_datalayer(datalayer)
        assert result['ga4_events']['Purchase'] == 1

    def test_ecommerce_event(self, auditor):
        datalayer = [{'event': 'checkout', 'ecommerce': {'items': []}}]
        result = auditor._parse_datalayer(datalayer)
        assert len(result['ecommerce_events']) == 1
        assert result['events'][0]['type'] == 'ecommerce'

    def test_custom_event(self, auditor):
        datalayer = [{'event': 'newsletter_signup', 'email_hash': 'abc'}]
        result = auditor._parse_datalayer(datalayer)
        assert 'newsletter_signup' in result['custom_events']
        assert result['events'][0]['type'] == 'custom'

    def test_mixed_events(self, auditor):
        datalayer = [
            {'event': 'page_view'},
            {'event': 'add_to_cart', 'item_id': '123'},
            {'event': 'custom_click', 'element': 'cta'},
            {'event': 'purchase', 'value': 50},
        ]
        result = auditor._parse_datalayer(datalayer)
        assert result['total_events'] == 4
        assert result['ga4_events']['Page View'] == 1
        assert result['ga4_events']['Add to Cart'] == 1
        assert result['ga4_events']['Purchase'] == 1
        assert 'custom_click' in result['custom_events']

    def test_non_dict_items_skipped(self, auditor):
        datalayer = ['not a dict', 42, {'event': 'page_view'}]
        result = auditor._parse_datalayer(datalayer)
        assert result['total_events'] == 3
        assert len(result['events']) == 1

    def test_missing_event_key(self, auditor):
        datalayer = [{'page': '/about', 'title': 'About'}]
        result = auditor._parse_datalayer(datalayer)
        assert result['events'][0]['event'] == 'unknown'
        assert result['events'][0]['type'] == 'custom'

    def test_duplicate_events_counted(self, auditor):
        datalayer = [
            {'event': 'page_view'},
            {'event': 'page_view'},
            {'event': 'page_view'},
        ]
        result = auditor._parse_datalayer(datalayer)
        assert result['ga4_events']['Page View'] == 3


class TestGtagArgumentDecoding:
    def test_gtag_event_purchase(self, auditor):
        """gtag('event','purchase',{value:99.99}) as arguments object."""
        datalayer = [{'0': 'event', '1': 'purchase', '2': {'value': 99.99, 'currency': 'USD'}}]
        result = auditor._parse_datalayer(datalayer)
        assert result['ga4_events']['Purchase'] == 1
        event = result['events'][0]
        assert event['event'] == 'purchase'
        assert event['type'] == 'ga4'
        assert event['data']['value'] == 99.99
        assert event.get('source') == 'gtag_arguments'

    def test_gtag_config_routes_to_config_summary(self, auditor):
        """gtag('config','G-ABC123') goes to gtag_config, not events."""
        datalayer = [{'0': 'config', '1': 'G-ABC123'}]
        result = auditor._parse_datalayer(datalayer)
        assert len(result['events']) == 0
        assert len(result['gtag_config']) == 1
        assert result['gtag_config'][0]['command'] == 'config'
        assert result['gtag_config'][0]['target'] == 'G-ABC123'

    def test_gtag_consent_routes_to_config_summary(self, auditor):
        """gtag('consent','default',{...}) goes to gtag_config."""
        datalayer = [{'0': 'consent', '1': 'default', '2': {'analytics_storage': 'denied'}}]
        result = auditor._parse_datalayer(datalayer)
        assert len(result['events']) == 0
        assert len(result['gtag_config']) == 1
        assert result['gtag_config'][0]['command'] == 'consent'
        assert result['gtag_config'][0]['params']['analytics_storage'] == 'denied'

    def test_gtag_event_conversion(self, auditor):
        """Custom conversion event via gtag arguments object."""
        datalayer = [{'0': 'event', '1': 'conversion_event_submit_lead_form',
                      '2': {'send_to': 'G-ABC123'}}]
        result = auditor._parse_datalayer(datalayer)
        assert len(result['events']) == 1
        assert result['events'][0]['event'] == 'conversion_event_submit_lead_form'
        assert result['events'][0]['type'] == 'custom'
        assert 'conversion_event_submit_lead_form' in result['custom_events']

    def test_regular_event_key_still_works(self, auditor):
        """Standard dataLayer push with 'event' key unchanged."""
        datalayer = [{'event': 'gtm.dom', 'gtm.uniqueEventId': 1}]
        result = auditor._parse_datalayer(datalayer)
        assert result['events'][0]['event'] == 'gtm.dom'
        assert result['events'][0]['type'] == 'custom'

    def test_mixed_datalayer_with_both_shapes(self, auditor):
        """dataLayer with both regular pushes and gtag argument objects."""
        datalayer = [
            {'event': 'page_view'},
            {'0': 'config', '1': 'G-ABC123'},
            {'0': 'event', '1': 'scroll'},
            {'event': 'custom_click', 'element': 'cta'},
            {'0': 'consent', '1': 'default', '2': {'ad_storage': 'denied'}},
        ]
        result = auditor._parse_datalayer(datalayer)
        event_names = [e['event'] for e in result['events']]
        assert 'page_view' in event_names
        assert 'scroll' in event_names
        assert 'custom_click' in event_names
        assert len(result['gtag_config']) == 2
        assert result['ga4_events']['Page View'] == 1
        assert result['ga4_events']['Scroll Tracking'] == 1

    def test_gtag_js_command_routes_to_config(self, auditor):
        """gtag('js', new Date()) serialized as arguments object."""
        datalayer = [{'0': 'js', '1': '2025-01-01T00:00:00.000Z'}]
        result = auditor._parse_datalayer(datalayer)
        assert len(result['events']) == 0
        assert len(result['gtag_config']) == 1
        assert result['gtag_config'][0]['command'] == 'js'

    def test_gtag_js_with_gtm_unique_event_id(self, auditor):
        """gtag('js', new Date()) with GTM-injected gtm.uniqueEventId.

        GTM adds non-numeric keys like gtm.uniqueEventId to the pushed object.
        This must still be recognized as a gtag arguments object and route to
        gtag_config, not fall through as unknown.
        """
        datalayer = [{'0': 'js', '1': '2025-01-01T00:00:00.000Z', 'gtm.uniqueEventId': 4}]
        result = auditor._parse_datalayer(datalayer)
        assert len(result['events']) == 0
        assert len(result['gtag_config']) == 1
        assert result['gtag_config'][0]['command'] == 'js'
        assert 'unknown' not in result['custom_events']


class TestGA4CollectDecoder:
    def test_decode_page_view_from_query_string(self, auditor):
        requests = [
            {'url': 'https://www.google-analytics.com/g/collect?v=2&tid=G-ABC123&en=page_view&dl=https://example.com/',
             'method': 'GET', 'type': 'ping', 'post_data': None},
        ]
        result = auditor.decode_ga4_collect_requests(requests)
        assert result['events']['page_view'] == 1
        assert 'G-ABC123' in result['measurement_ids']

    def test_decode_multiple_events(self, auditor):
        requests = [
            {'url': 'https://www.google-analytics.com/g/collect?v=2&tid=G-ABC123&en=page_view',
             'method': 'GET', 'type': 'ping', 'post_data': None},
            {'url': 'https://www.google-analytics.com/g/collect?v=2&tid=G-ABC123&en=scroll',
             'method': 'GET', 'type': 'ping', 'post_data': None},
        ]
        result = auditor.decode_ga4_collect_requests(requests)
        assert result['events']['page_view'] == 1
        assert result['events']['scroll'] == 1
        assert result['raw_request_count'] == 2

    def test_decode_post_body(self, auditor):
        requests = [
            {'url': 'https://www.google-analytics.com/g/collect',
             'method': 'POST', 'type': 'ping',
             'post_data': 'v=2&tid=G-ABC123&en=conversion_event_submit_lead_form&ep.form_id=contact'},
        ]
        result = auditor.decode_ga4_collect_requests(requests)
        assert result['events']['conversion_event_submit_lead_form'] == 1
        detail = result['event_details'][0]
        assert detail['params']['form_id'] == 'contact'

    def test_decode_measurement_id(self, auditor):
        requests = [
            {'url': 'https://www.google-analytics.com/g/collect?v=2&tid=G-XYZ789&en=page_view',
             'method': 'GET', 'type': 'ping', 'post_data': None},
        ]
        result = auditor.decode_ga4_collect_requests(requests)
        assert result['measurement_ids'] == ['G-XYZ789']

    def test_decode_event_params(self, auditor):
        requests = [
            {'url': 'https://www.google-analytics.com/g/collect?v=2&tid=G-ABC123&en=scroll&ep.percent_scrolled=90',
             'method': 'GET', 'type': 'ping', 'post_data': None},
        ]
        result = auditor.decode_ga4_collect_requests(requests)
        detail = result['event_details'][0]
        assert detail['params']['percent_scrolled'] == '90'

    def test_no_collect_requests_returns_empty(self, auditor):
        requests = [
            {'url': 'https://cdn.example.com/style.css',
             'method': 'GET', 'type': 'stylesheet', 'post_data': None},
        ]
        result = auditor.decode_ga4_collect_requests(requests)
        assert result['events'] == {}
        assert result['measurement_ids'] == []
        assert result['raw_request_count'] == 0

    def test_custom_event_names_preserved(self, auditor):
        requests = [
            {'url': 'https://www.google-analytics.com/g/collect?v=2&tid=G-ABC123&en=conversion_event_submit_lead_form',
             'method': 'GET', 'type': 'ping', 'post_data': None},
        ]
        result = auditor.decode_ga4_collect_requests(requests)
        assert 'conversion_event_submit_lead_form' in result['events']
        # It's not in GA4_EVENTS so no description, but name is preserved
        detail = result['event_details'][0]
        assert detail['name'] == 'conversion_event_submit_lead_form'

    def test_deduplication_of_retransmissions(self, auditor):
        """_s=1 and _s=2 retransmissions should be counted once."""
        requests = [
            {'url': 'https://www.google-analytics.com/g/collect?v=2&tid=G-ABC123&en=page_view&dl=https://example.com/&_s=1',
             'method': 'GET', 'type': 'ping', 'post_data': None},
            {'url': 'https://www.google-analytics.com/g/collect?v=2&tid=G-ABC123&en=page_view&dl=https://example.com/&_s=2',
             'method': 'GET', 'type': 'ping', 'post_data': None},
        ]
        result = auditor.decode_ga4_collect_requests(requests)
        assert result['events']['page_view'] == 1
        assert result['raw_request_count'] == 2
        assert len(result['event_details']) == 1
