# Changelog

All notable changes to FBS (Fayvad Business Suite) will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [2.0.6] - 2025-01-06

### Critical Fixes
- Added missing `search_read` method to `OdooIntegrationInterface`
- Implemented automatic model name mapping (`inventory.location` → `stock.location`)
- Enhanced all CRUD methods with model mapping for compatibility
- Fixed 6 critical rental management endpoints that were failing
- Resolved production-blocking issues for rental integration team

### Documentation
- Added `RENTAL_ENDPOINTS_FIX_GUIDE.md` with implementation examples
- Created comprehensive `FBS_v2.0.6_RELEASE_NOTES.md`
- Updated all version references across documentation

### Technical Improvements
- Model name mapping system for deprecated Odoo model references
- Backward-compatible interface enhancements
- Production-ready hotfix for critical integration failures

## [2.0.5] - 2025-01-15

### Fixed
- **CRITICAL:** Fixed DMS views assuming `request.user.company_id` exists (prevents AttributeError)
- Fixed AuthService constructor to accept optional solution_name parameter
- Fixed undefined variable reference in auth service logging
- Standardized logging across all services to use consistent 'fbs_app' logger

### Changed  
- Improved error handling with safe attribute access in DMS views
- Enhanced system reliability across all three modules (fbs_app, fbs_dms, fbs_license_manager)

### Verified
- Comprehensive multi-module system verification completed
- All cross-module dependencies confirmed safe (no circular imports)
- All model relationships validated with proper on_delete parameters
- All method signatures verified to match implementations
- Complete production readiness confirmed across entire FBS suite

## [2.0.4] - Previous Release

### Added
- Comprehensive documentation alignment with current implementation
- Modern Python packaging with pyproject.toml
- Support for all three core apps: FBS, DMS, and License Manager
- Development and testing dependency groups

### Changed
- Updated package name from `fbs-app` to `fbs-suite`
- Restructured requirements for production vs. development use
- Enhanced setup.py with proper app inclusion

## [2.0.1] - 2024-08-27

### Fixed
- **Critical Odoo Integration Issues**: Fixed all blocking bugs that prevented Odoo integration from working
- **Constructor Mismatches**: All FBS services now properly accept `solution_name` parameter
- **Missing Methods**: Added `get_database_info()` and `discover_fields()` methods
- **Method Return Values**: Methods no longer return `False`, now return proper error structures
- **Response Format Standardization**: All methods return consistent response structures
- **Database Table Creation**: Added `create_fbs_tables()` method for required FBS infrastructure

### Added
- **OdooClient Enhancements**: `get_database_info()` and `is_available()` methods
- **DiscoveryService Improvements**: `discover_fields()` method and proper constructor
- **DatabaseService Features**: `create_fbs_tables()` method for FBS table management
- **Interface Consistency**: All interfaces properly pass `solution_name` to services

### Changed
- **Service Architecture**: Standardized constructor patterns across all services
- **Error Handling**: Implemented robust error handling with proper response structures
- **Method Signatures**: Standardized method signatures across all services and interfaces
- **Database Integration**: Improved FBS table creation and management capabilities

### Technical Improvements
- **Constructor Consistency**: All services follow the same parameter pattern
- **Error Response Standardization**: Consistent error response format across all methods
- **Service Layer Alignment**: Proper alignment between interfaces and service implementations
- **Database Infrastructure**: Complete FBS table creation system

## [2.0.0] - 2024-08-27

### Added
- Odoo-driven architecture implementation
- FBS Virtual Fields system for custom data extensions
- Document Management System (DMS) with Odoo integration
- License Manager with feature control and usage tracking
- Multi-tenant solution architecture
- Comprehensive business intelligence capabilities
- Workflow management and approval systems
- MSME business management tools
- Accounting and financial operations
- Caching and performance optimization

### Changed
- Migrated from Django-only to Odoo + Virtual Fields + Django UI
- Restructured service layer architecture
- Implemented solution-based database routing
- Enhanced security and authentication systems

### Deprecated
- Legacy Django-only models and services
- Old API endpoint approach

### Removed
- Outdated REST API endpoints
- Unused Django models and services

## [1.0.0] - 2024-12-01

### Added
- Initial Django application structure
- Basic business management models
- MSME business tools
- Simple accounting functionality
- Basic workflow management

### Changed
- N/A

### Deprecated
- N/A

### Removed
- N/A

---

## Installation Instructions

### From Git Repository
```bash
# Clone the repository
git clone https://github.com/kuriadn/fbs.git
cd fbs

# Install in development mode
pip install -e .

# Install with development dependencies
pip install -e ".[dev]"

# Install with testing dependencies
pip install -e ".[test]"

# Install with documentation dependencies
pip install -e ".[docs]"
```

### From PyPI (when available)
```bash
# Install production version
pip install fbs-suite

# Install with development dependencies
pip install fbs-suite[dev]

# Install with testing dependencies
pip install fbs-suite[test]
```

## Migration Guide

### From v1.x to v2.0
- Major architectural changes from Django-only to Odoo-driven
- New service interface approach replaces old API endpoints
- Virtual Fields system for custom data extensions
- Updated configuration and settings structure

### From v2.0-beta to v2.0
- Stable API interfaces
- Enhanced error handling and validation
- Improved performance and caching
- Comprehensive testing coverage

## Support

For support and questions:
- Check the [documentation](https://github.com/kuriadn/fbs/tree/main/docs)
- Create an issue in the [GitHub repository](https://github.com/kuriadn/fbs/issues)
- Contact the development team at dev@fayvad.com
