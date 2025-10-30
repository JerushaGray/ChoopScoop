#!/usr/bin/env python3
"""
Site Auditor v2.1 - Professional Web Crawler & Tag Detection Tool
Fixed: Cross-platform dependency checking for Playwright browsers (Windows/macOS/Linux)
"""

import asyncio
import json
import csv
import re
import subprocess
import logging
import argparse
import sys
from pathlib import Path
from urllib.parse import urljoin, urlparse
from datetime import datetime
from collections import defaultdict
from typing import Set, Dict, List, Optional, Tuple
from platform import system

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

    # ✅ Cross-platform check for Playwright browsers
    if system() == "Windows":
        playwright_dir = Path.home() / "AppData" / "Local" / "ms-playwright"
    else:
        playwright_dir = Path.home() / ".cache" / "ms-playwright"

    if not playwright_dir.exists() or not any(playwright_dir.glob("chromium-*")):
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
            ["wappalyzer", "--version"],
            capture_output=True,
            timeout=5,
            text=True
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


# ... (The rest of your original code remains unchanged)
