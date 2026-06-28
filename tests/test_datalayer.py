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
