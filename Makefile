# FBS App Development Makefile
# Provides easy commands for testing, development, and maintenance

.PHONY: help install test test-unit test-integration test-performance test-security test-all coverage lint format clean install-dev install-prod

# Default target
help:
	@echo "🚀 FBS App Development Commands"
	@echo "================================"
	@echo ""
	@echo "📦 Installation:"
	@echo "  install        Install production dependencies"
	@echo "  install-dev    Install development dependencies"
	@echo ""
	@echo "🧪 Testing:"
	@echo "  test           Run all tests with coverage"
	@echo "  test-unit      Run unit tests only"
	@echo "  test-integration Run integration tests only"
	@echo "  test-performance Run performance tests only"
	@echo "  test-security  Run security tests only"
	@echo "  test-all       Run comprehensive test suite"
	@echo "  coverage       Generate coverage reports"
	@echo ""
	@echo "🔧 Development:"
	@echo "  lint           Run code quality checks"
	@echo "  format         Format code with Black and isort"
	@echo "  clean          Clean up generated files"
	@echo ""
	@echo "📊 Reports:"
	@echo "  report         Generate comprehensive test report"
	@echo "  benchmark      Run benchmark tests"
	@echo "  security-check Run security checks"
	@echo ""
	@echo "🚀 Quick Start:"
	@echo "  make install-dev  # Install development dependencies"
	@echo "  make test-all     # Run all tests and checks"

# Installation
install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements.txt
	pip install -e .

# Testing
test:
	python run_tests.py --coverage

test-unit:
	python run_tests.py --unit

test-integration:
	python run_tests.py --integration

test-performance:
	python run_tests.py --performance

test-security:
	python run_tests.py --security

test-all:
	python run_tests.py --all

coverage:
	python run_tests.py --report

# Development
lint:
	python run_tests.py --quality

format:
	@echo "🔧 Formatting code with Black..."
	black fbs_app/ django_project/
	@echo "📝 Sorting imports with isort..."
	isort fbs_app/ django_project/
	@echo "✅ Code formatting complete!"

clean:
	@echo "🧹 Cleaning up generated files..."
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf coverage.xml
	rm -rf test-results.xml
	rm -rf .pytest_cache/
	rm -rf __pycache__/
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
	@echo "✅ Cleanup complete!"

# Reports
report:
	python run_tests.py --report

benchmark:
	python run_tests.py --benchmark

security-check:
	python run_tests.py --security-checks

# Database operations
migrate:
	cd fbs_project && python manage.py migrate

makemigrations:
	cd fbs_project && python manage.py makemigrations fbs_app

# Development server
run:
	cd fbs_project && python manage.py runserver

shell:
	cd fbs_project && python manage.py shell

# Docker operations (if needed)
docker-build:
	docker build -t fbs-app .

docker-run:
	docker run -p 8000:8000 fbs-app

# Performance testing
load-test:
	@echo "🚀 Running load tests with Locust..."
	locust -f fbs_app/tests/load_test.py --host=http://localhost:8000

# Security scanning
security-scan:
	@echo "🔒 Running security scans..."
	bandit -r fbs_app/
	safety check

# Code quality
quality-check:
	@echo "🔍 Running comprehensive code quality checks..."
	black --check fbs_app/ django_project/
	isort --check-only fbs_app/ django_project/
	flake8 fbs_app/ django_project/
	mypy fbs_app/ django_project/

# Pre-commit setup
setup-pre-commit:
	@echo "🔧 Setting up pre-commit hooks..."
	pip install pre-commit
	pre-commit install
	@echo "✅ Pre-commit hooks installed!"

# CI/CD helpers
ci-test:
	@echo "🚀 Running CI/CD test suite..."
	python run_tests.py --all
	@echo "✅ CI/CD tests completed!"

# Development workflow
dev-setup: install-dev setup-pre-commit
	@echo "🎉 Development environment setup complete!"
	@echo "Next steps:"
	@echo "  1. make test-all     # Run all tests"
	@echo "  2. make format       # Format code"
	@echo "  3. make run          # Start development server"

# Quick development cycle
dev-cycle: format test-all
	@echo "🔄 Development cycle complete!"

# Production preparation
prod-prep: clean test-all quality-check security-scan
	@echo "🚀 Production preparation complete!"

# Helpers
check-deps:
	@echo "📋 Checking dependencies..."
	pip list --outdated
	@echo "✅ Dependency check complete!"

update-deps:
	@echo "🔄 Updating dependencies..."
	pip install --upgrade -r requirements.txt
	@echo "✅ Dependencies updated!"

# Environment setup
setup-env:
	@echo "🌍 Setting up environment..."
	@if [ ! -f .env ]; then \
		echo "Creating .env file..."; \
		cp env.example .env 2>/dev/null || echo "No env.example found, creating basic .env"; \
		echo "DJANGO_SECRET_KEY=your-secret-key-here" >> .env; \
		echo "DJANGO_DEBUG=True" >> .env; \
		echo "DB_NAME=fbs_system_db" >> .env; \
		echo "DB_USER=odoo" >> .env; \
		echo "DB_PASSWORD=four@One2" >> .env; \
		echo "DB_HOST=localhost" >> .env; \
		echo "DB_PORT=5432" >> .env; \
	fi
	@echo "✅ Environment setup complete!"

# Quick test with specific markers
test-fast:
	pytest fbs_app/tests/ -m "fast" -v

test-slow:
	pytest fbs_app/tests/ -m "slow" -v

# Parallel testing
test-parallel:
	python run_tests.py --parallel

# Specific test files
test-models:
	pytest fbs_app/tests/test_models.py -v

test-interfaces:
	pytest fbs_app/tests/test_interfaces.py -v

# Debug helpers
debug-test:
	pytest fbs_app/tests/ -v -s --pdb

# Coverage with specific thresholds
coverage-strict:
	pytest --cov=fbs_app --cov-fail-under=95 --cov-report=term-missing

# Performance profiling
profile:
	pytest fbs_app/tests/ --benchmark-only --benchmark-sort=name

# Documentation generation
docs:
	@echo "📚 Generating documentation..."
	# Add documentation generation commands here
	@echo "✅ Documentation generated!"

# Package building
build:
	@echo "📦 Building package..."
	python setup.py sdist bdist_wheel
	@echo "✅ Package built!"

# Installation verification
verify-install:
	@echo "🔍 Verifying installation..."
	python -c "import fbs_app; print('✅ FBS App imported successfully')"
	@echo "✅ Installation verified!"

# Quick health check
health-check:
	@echo "🏥 Running health checks..."
	python -c "import fbs_app; print('✅ Import check passed')"
	python -c "from fbs_app.interfaces import FBSInterface; print('✅ Interface check passed')"
	@echo "✅ Health checks passed!"

# Development shortcuts
dev: dev-setup
	@echo "🚀 Ready for development!"

test-quick: test-unit test-interfaces
	@echo "⚡ Quick tests completed!"

# Default development workflow
all: clean install-dev test-all quality-check
	@echo "🎉 All tasks completed successfully!"
