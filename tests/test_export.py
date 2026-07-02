"""Tests for export functionality (JSON, CSV, HTML)."""

import csv
import json
import os
import tempfile
import pytest


class TestJsonExport:
    def test_export_creates_file(self, auditor):
        auditor.page_data = [
            {'url': 'https://example.com', 'depth': 0, 'status': 200,
             'metadata': {'title': 'Home'}, 'tags': {}, 'datalayer': {},
             'technologies': [], 'performance': {}, 'network_requests': [],
             'internal_links_found': 3, 'screenshot': None,
             'crawled_at': '2025-01-01T00:00:00'}
        ]
        auditor.stats['pages_crawled'] = 1

        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            path = f.name

        try:
            auditor.export_json(path)
            with open(path) as f:
                data = json.load(f)

            assert data['crawl_info']['start_url'] == 'https://example.com'
            assert data['crawl_info']['total_pages'] == 1
            assert data['crawl_info']['pages_success'] == 1
            assert len(data['sitemap']) == 1
            assert data['sitemap'][0] == 'https://example.com'
            assert len(data['pages']) == 1
        finally:
            os.unlink(path)

    def test_export_empty_crawl(self, auditor):
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            path = f.name

        try:
            auditor.export_json(path)
            with open(path) as f:
                data = json.load(f)

            assert data['crawl_info']['total_pages'] == 0
            assert data['pages'] == []
            assert data['sitemap'] == []
        finally:
            os.unlink(path)


class TestCsvExport:
    def _make_page(self, url='https://example.com', tags=None):
        return {
            'url': url, 'depth': 0, 'status': 200,
            'metadata': {'title': 'Test Page', 'description': 'desc'},
            'tags': tags or {},
            'datalayer': {'total_events': 2, 'ga4_events': {'Page View': 1}, 'ecommerce_events': []},
            'technologies': [{'name': 'react', 'category': 'JavaScript Framework'}],
            'performance': {'load_time': 1234.5},
            'internal_links_found': 5,
        }

    def test_csv_creates_file_with_header(self, auditor):
        auditor.page_data = [self._make_page()]

        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False, mode='w') as f:
            path = f.name

        try:
            auditor.export_csv(path)
            with open(path, newline='') as f:
                reader = csv.DictReader(f)
                rows = list(reader)

            assert len(rows) == 1
            assert rows[0]['url'] == 'https://example.com'
            assert rows[0]['load_time_ms'] == '1234'
            assert rows[0]['technologies'] == '1'
        finally:
            os.unlink(path)

    def test_csv_tag_columns(self, auditor):
        tags = {
            'google_tag_manager': {'found': True, 'ids': ['GTM-ABC'], 'category': 'Tag Management'},
            'google_analytics_4': {'found': True, 'ids': ['G-123'], 'category': 'Analytics'},
        }
        auditor.page_data = [self._make_page(tags=tags)]

        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False, mode='w') as f:
            path = f.name

        try:
            auditor.export_csv(path)
            with open(path, newline='') as f:
                reader = csv.DictReader(f)
                row = next(reader)

            assert row['gtm'] == 'Yes'
            assert row['ga4'] == 'Yes'
            assert row['facebook_pixel'] == 'No'
            assert row['tags_total'] == '2'
        finally:
            os.unlink(path)

    def test_csv_empty_data_no_file(self, auditor):
        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False, mode='w') as f:
            path = f.name

        auditor.export_csv(path)
        # File exists but should have no content rows (export_csv returns early)
        with open(path) as f:
            content = f.read()
        assert content == ''
        os.unlink(path)


class TestHtmlExport:
    def test_html_contains_domain(self, auditor):
        auditor.page_data = [
            {'url': 'https://example.com', 'depth': 0, 'status': 200,
             'metadata': {'title': 'Home'}, 'tags': {}, 'datalayer': {},
             'technologies': [], 'performance': {}, 'network_requests': [],
             'internal_links_found': 0, 'screenshot': None,
             'crawled_at': '2025-01-01T00:00:00'}
        ]

        with tempfile.NamedTemporaryFile(suffix='.html', delete=False) as f:
            path = f.name

        try:
            auditor.export_html(path)
            with open(path) as f:
                html = f.read()

            assert 'example.com' in html
            assert '<html>' in html
            assert 'Site Audit Report' in html
        finally:
            os.unlink(path)

    def test_html_shows_detected_tags(self, auditor):
        auditor.page_data = [
            {'url': 'https://example.com', 'depth': 0, 'status': 200,
             'metadata': {'title': 'Home'},
             'tags': {'google_tag_manager': {'found': True, 'ids': ['GTM-ABC'], 'category': 'Tag Management'}},
             'datalayer': {}, 'technologies': [], 'performance': {},
             'network_requests': [], 'internal_links_found': 0,
             'screenshot': None, 'crawled_at': '2025-01-01T00:00:00'}
        ]

        with tempfile.NamedTemporaryFile(suffix='.html', delete=False) as f:
            path = f.name

        try:
            auditor.export_html(path)
            with open(path) as f:
                html = f.read()

            assert 'Google Tag Manager' in html
            assert 'Tags Detected' in html
        finally:
            os.unlink(path)


class TestTagMatrixExport:
    def _make_page(self, url, tags):
        return {
            'url': url, 'depth': 0, 'status': 200,
            'metadata': {'title': 'Test'}, 'tags': tags,
            'datalayer': {}, 'technologies': [], 'performance': {},
            'network_requests': [], 'internal_links_found': 0,
            'screenshot': None, 'crawled_at': '2025-01-01T00:00:00',
        }

    def test_matrix_creates_csv(self, auditor):
        tags = {
            'google_tag_manager': {'found': True, 'ids': ['GTM-ABC'], 'category': 'Tag Management'},
            'facebook_pixel': {'found': False},
        }
        auditor.page_data = [self._make_page('https://example.com', tags)]

        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as f:
            path = f.name
        try:
            auditor.export_tag_matrix(path)
            with open(path, newline='') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
            # 1 page row + 1 summary row
            assert len(rows) == 2
            assert rows[0]['google_tag_manager'] == 'x'
            assert 'facebook_pixel' not in reader.fieldnames
            assert rows[1]['page'] == 'TOTAL'
            assert rows[1]['google_tag_manager'] == '1'
        finally:
            os.unlink(path)

    def test_matrix_groups_identical_profiles(self, auditor):
        tags_full = {
            'google_tag_manager': {'found': True, 'ids': [], 'category': 'Tag Management'},
            'google_analytics_4': {'found': True, 'ids': [], 'category': 'Analytics'},
        }
        tags_partial = {
            'google_tag_manager': {'found': True, 'ids': [], 'category': 'Tag Management'},
            'google_analytics_4': {'found': False},
        }
        auditor.page_data = [
            self._make_page('https://example.com/', tags_full),
            self._make_page('https://example.com/about', tags_full),
            self._make_page('https://example.com/blog', tags_partial),
        ]

        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as f:
            path = f.name
        try:
            auditor.export_tag_matrix(path)
            with open(path, newline='') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
            # 2 profile rows + 1 summary
            assert len(rows) == 3
            # First row is the group of 2
            assert rows[0]['pages_in_group'] == '2'
            assert '+1 more' in rows[0]['page']
            assert rows[0]['google_analytics_4'] == 'x'
            # Second row is the single page missing GA4
            assert rows[1]['pages_in_group'] == '1'
            assert rows[1]['google_analytics_4'] == ''
            assert rows[1]['google_tag_manager'] == 'x'
        finally:
            os.unlink(path)

    def test_matrix_empty_data(self, auditor):
        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as f:
            path = f.name
        auditor.export_tag_matrix(path)
        with open(path) as f:
            assert f.read() == ''
        os.unlink(path)

    def test_matrix_summary_row_counts(self, auditor):
        tags_a = {
            'google_tag_manager': {'found': True, 'ids': [], 'category': 'Tag Management'},
            'hotjar': {'found': True, 'ids': [], 'category': 'Heatmaps'},
        }
        tags_b = {
            'google_tag_manager': {'found': True, 'ids': [], 'category': 'Tag Management'},
            'hotjar': {'found': False},
        }
        auditor.page_data = [
            self._make_page('https://example.com/', tags_a),
            self._make_page('https://example.com/about', tags_a),
            self._make_page('https://example.com/blog', tags_b),
        ]

        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as f:
            path = f.name
        try:
            auditor.export_tag_matrix(path)
            with open(path, newline='') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
            summary = rows[-1]
            assert summary['page'] == 'TOTAL'
            assert summary['google_tag_manager'] == '3'
            assert summary['hotjar'] == '2'
        finally:
            os.unlink(path)


class TestNetworkRequestClassification:
    def test_owned_domain_excluded_from_unidentified(self, auditor):
        """Hosts on a vendor's owned_domains list are not unidentified."""
        auditor.page_data = [
            {'url': 'https://example.com', 'depth': 0, 'status': 200,
             'metadata': {}, 'tags': {}, 'datalayer': {},
             'technologies': [], 'performance': {},
             'network_requests': [
                 {'url': 'https://secure.quantserve.com/pixel/abc.gif',
                  'method': 'GET', 'type': 'image', 'post_data': None},
                 {'url': 'https://rules.quantcount.com/rules.js',
                  'method': 'GET', 'type': 'script', 'post_data': None},
                 {'url': 'https://js.hs-analytics.net/analytics.js',
                  'method': 'GET', 'type': 'script', 'post_data': None},
                 {'url': 'https://track.hubspot.com/__ptq.gif',
                  'method': 'GET', 'type': 'image', 'post_data': None},
             ],
             'internal_links_found': 0, 'screenshot': None,
             'crawled_at': '2025-01-01T00:00:00'}
        ]
        matched, unidentified = auditor._classify_network_requests()
        assert len(matched) == 4
        assert len(unidentified) == 0

    def test_unknown_vendor_remains_in_unidentified(self, auditor):
        """Hosts matching no owned_domains entry stay in unidentified."""
        auditor.page_data = [
            {'url': 'https://example.com', 'depth': 0, 'status': 200,
             'metadata': {}, 'tags': {}, 'datalayer': {},
             'technologies': [], 'performance': {},
             'network_requests': [
                 {'url': 'https://tracking.unknown-vendor.com/pixel.gif',
                  'method': 'GET', 'type': 'image', 'post_data': None},
                 {'url': 'https://sync.mystery-adtech.net/id?abc=1',
                  'method': 'GET', 'type': 'image', 'post_data': None},
             ],
             'internal_links_found': 0, 'screenshot': None,
             'crawled_at': '2025-01-01T00:00:00'}
        ]
        matched, unidentified = auditor._classify_network_requests()
        assert len(matched) == 0
        assert 'tracking.unknown-vendor.com' in unidentified
        assert 'sync.mystery-adtech.net' in unidentified

    def test_mixed_known_and_unknown_hosts(self, auditor):
        """Known vendor hosts are matched, unknown hosts are unidentified."""
        auditor.page_data = [
            {'url': 'https://example.com', 'depth': 0, 'status': 200,
             'metadata': {}, 'tags': {}, 'datalayer': {},
             'technologies': [], 'performance': {},
             'network_requests': [
                 {'url': 'https://px.ads.linkedin.com/collect?pid=123',
                  'method': 'GET', 'type': 'image', 'post_data': None},
                 {'url': 'https://snap.licdn.com/li.lms-analytics/insight.min.js',
                  'method': 'GET', 'type': 'script', 'post_data': None},
                 {'url': 'https://unknown-adtech.example.net/pixel.gif',
                  'method': 'GET', 'type': 'image', 'post_data': None},
             ],
             'internal_links_found': 0, 'screenshot': None,
             'crawled_at': '2025-01-01T00:00:00'}
        ]
        matched, unidentified = auditor._classify_network_requests()
        assert len(matched) == 2
        assert 'unknown-adtech.example.net' in unidentified
        assert 'px.ads.linkedin.com' not in unidentified
        assert 'snap.licdn.com' not in unidentified
