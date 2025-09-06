#!/bin/bash

# FBS Suite v2.0.6 Release Script
# This script creates a git tag and release for version 2.0.6

set -e

echo "🚀 FBS Suite v2.0.6 Release Process"
echo "==================================="

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    echo "❌ Error: Not in FBS root directory"
    exit 1
fi

# Verify version numbers are updated
if ! grep -q 'version = "2.0.6"' pyproject.toml; then
    echo "❌ Error: pyproject.toml version not updated to 2.0.6"
    exit 1
fi

if ! grep -q "version='2.0.6'" setup.py; then
    echo "❌ Error: setup.py version not updated to 2.0.6"
    exit 1
fi

echo "✅ Version numbers verified"

# Check git status
if ! git diff --quiet; then
    echo "⚠️  Warning: Uncommitted changes detected"
    echo "📝 Committing changes..."
    git add .
    git commit -m "🚀 Release FBS Suite v2.0.6 - Critical Hotfix

- Fixed missing search_read method in OdooIntegrationInterface
- Implemented automatic model name mapping (inventory.location → stock.location)
- Resolved 6 critical rental management endpoint failures
- Added comprehensive implementation guide for rental team
- Updated all version references to 2.0.6

This is a critical hotfix release that restores full functionality
to rental management systems and other dependent applications."
fi

echo "📝 Creating git tag v2.0.6..."
git tag -a v2.0.6 -m "FBS Suite v2.0.6 - Critical Hotfix

Critical fixes for rental integration team:
- Added missing search_read method to OdooIntegrationInterface
- Fixed invalid inventory.location model reference with automatic mapping
- Enhanced all CRUD methods with model name mapping
- Resolved production-blocking issues for 6 endpoints
- Comprehensive implementation guide provided

This hotfix release restores full functionality to dependent systems."

echo "✅ Git tag v2.0.6 created"

echo "🚀 Pushing to remote repository..."
git push origin main
git push origin v2.0.6

echo "🎉 FBS Suite v2.0.6 Release Complete!"
echo "=================================="
echo "   • Version: 2.0.6"
echo "   • Release Type: Critical Hotfix"
echo "   • Release Notes: FBS_v2.0.6_RELEASE_NOTES.md"
echo "   • Implementation Guide: RENTAL_ENDPOINTS_FIX_GUIDE.md"
echo "   • Git Tag: v2.0.6"
echo ""
echo "📋 Next Steps:"
echo "   1. Rental team can deploy FBS Suite 2.0.6"
echo "   2. Follow RENTAL_ENDPOINTS_FIX_GUIDE.md for implementation"
echo "   3. Test all endpoints to verify fixes"
echo "   4. Deploy to production with confidence"
echo ""
echo "🚀 Production-ready release available!"
