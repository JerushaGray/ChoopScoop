#!/bin/bash

# Site Auditor v2.1 - Installation Script
echo "🚀 Site Auditor v2.1 - Installation"
echo "===================================="
echo ""

# Check Python
echo "✓ Checking Python..."
python3 --version
if [ $? -ne 0 ]; then
    echo "❌ Python 3.7+ is required"
    exit 1
fi
echo ""

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install playwright pyyaml --break-system-packages 2>/dev/null || pip install playwright pyyaml
if [ $? -ne 0 ]; then
    echo "❌ Failed to install Python dependencies"
    exit 1
fi
echo ""

# Install Playwright browsers
echo "🌐 Installing Playwright browsers..."
playwright install chromium
if [ $? -ne 0 ]; then
    echo "❌ Failed to install Playwright browsers"
    exit 1
fi
echo ""

# Check Node.js (optional)
echo "✓ Checking Node.js (optional)..."
node --version 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️  Node.js not found"
    echo "   Wappalyzer won't be available (technology detection limited)"
    echo "   Install from: https://nodejs.org/"
    echo ""
    echo "   You can still use the tool with built-in patterns!"
    echo ""
else
    # Install Wappalyzer
    echo "📦 Installing Wappalyzer CLI..."
    npm install -g wappalyzer 2>/dev/null
    if [ $? -ne 0 ]; then
        echo "⚠️  Wappalyzer install failed"
        echo "   Technology detection will use fallback patterns"
        echo ""
    else
        echo "✓ Wappalyzer installed successfully"
        echo ""
    fi
fi

# Check if files exist
echo "✓ Checking required files..."
if [ ! -f "site_auditor_v2.1.py" ]; then
    echo "❌ site_auditor_v2.1.py not found"
    exit 1
fi

if [ ! -f "tag_patterns.py" ]; then
    echo "❌ tag_patterns.py not found"
    exit 1
fi
echo "   All required files present"
echo ""

# Make executable
chmod +x site_auditor_v2.1.py 2>/dev/null

echo "=" * 60
echo "✅ Installation complete!"
echo "=" * 60
echo ""
echo "🎯 Quick Start:"
echo "   python site_auditor_v2.1.py https://example.com"
echo ""
echo "📚 Documentation:"
echo "   • QUICK-START-v2.1.md - Quick reference"
echo "   • PATCH-NOTES-v2.1.md - What's fixed from v2.0"
echo "   • README_v2.md - Complete docs"
echo ""
echo "🔧 All options:"
echo "   python site_auditor_v2.1.py --help"
echo ""
echo "Happy auditing! 🔍"
