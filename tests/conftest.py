"""Shared fixtures for the ChoopScoop test suite."""

import pytest
from choopscoop.cli import _default_config


@pytest.fixture
def default_config():
    """A default config dict with a start_url set."""
    config = _default_config()
    config['start_url'] = 'https://example.com'
    config['resume']['enabled'] = False
    config['logging']['console'] = False
    config['logging']['log_file'] = None
    return config


@pytest.fixture
def auditor(default_config):
    """A SiteAuditor instance configured for testing (no Playwright needed)."""
    from choopscoop.auditor import SiteAuditor
    return SiteAuditor(default_config)
