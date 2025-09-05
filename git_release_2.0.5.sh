#!/bin/bash

# FBS Suite v2.0.5 Release Script
# This script creates a git tag and release for version 2.0.5

set -e

echo "🚀 FBS Suite v2.0.5 Release Process"
echo "=================================="

# Verify we're in the right directory
if [ ! -f "setup.py" ] || [ ! -f "pyproject.toml" ]; then
    echo "❌ Error: This script must be run from the FBS project root directory"
    exit 1
fi

# Check git status
if ! git diff --quiet; then
    echo "⚠️  Warning: You have uncommitted changes. Please commit or stash them first."
    echo "Uncommitted files:"
    git status --porcelain
    exit 1
fi

echo "✅ Git status clean"

# Verify version numbers are updated
if ! grep -q "version = \"2.0.5\"" pyproject.toml; then
    echo "❌ Error: pyproject.toml version not updated to 2.0.5"
    exit 1
fi

if ! grep -q "version='2.0.5'" setup.py; then
    echo "❌ Error: setup.py version not updated to 2.0.5"
    exit 1
fi

echo "✅ Version numbers verified"

# Create git tag
echo "📝 Creating git tag v2.0.5..."
git tag -a v2.0.5 -m "FBS Suite v2.0.5 - Critical Fixes and System Verification

🔧 Critical Fixes:
- Fixed DMS user.company_id AttributeError (CRITICAL)
- Fixed AuthService constructor parameter handling
- Standardized logging across all services
- Fixed variable reference in auth service

✅ System Verification:
- Comprehensive multi-module verification completed
- All cross-module dependencies confirmed safe
- Complete production readiness verified
- Zero remaining critical issues

This release ensures the entire FBS ecosystem is production-ready."

echo "✅ Git tag v2.0.5 created"

# Push tag to remote
echo "🌐 Pushing tag to remote repository..."
git push origin v2.0.5

echo "✅ Tag pushed to remote"

echo ""
echo "🎉 FBS Suite v2.0.5 Release Complete!"
echo "=================================="
echo ""
echo "📋 Release Summary:"
echo "   • Version: 2.0.5"
echo "   • Type: Patch Release - Critical Fixes"
echo "   • Status: Production Ready"
echo "   • All Modules: fbs_app, fbs_dms, fbs_license_manager"
echo ""
echo "📖 Documentation:"
echo "   • Release Notes: FBS_v2.0.5_RELEASE_NOTES.md"
echo "   • Changelog: CHANGELOG.md"
echo ""
echo "🚀 Next Steps:"
echo "   1. Verify tag appears in repository"
echo "   2. Create GitHub/GitLab release from tag"
echo "   3. Update package registries if applicable"
echo "   4. Notify stakeholders of release"
echo ""
