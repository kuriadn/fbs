#!/usr/bin/env python
"""
Comprehensive Test Runner for FBS App

This script provides multiple testing options:
- Unit tests only
- Integration tests only
- All tests with coverage
- Performance tests
- Security tests
- Custom test selection
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(command)}")
    print(f"{'='*60}\n")
    
    try:
        result = subprocess.run(command, check=True, capture_output=False)
        print(f"\n✅ {description} completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ {description} failed with exit code {e.returncode}")
        return False

def run_unit_tests():
    """Run unit tests only"""
    command = [
        "python", "-m", "pytest",
        "fbs_app/tests/test_models.py",
        "fbs_app/tests/test_interfaces.py",
        "-m", "unit",
        "--tb=short",
        "-v"
    ]
    return run_command(command, "Unit Tests")

def run_integration_tests():
    """Run integration tests only"""
    command = [
        "python", "-m", "pytest",
        "fbs_app/tests/",
        "-m", "integration",
        "--tb=short",
        "-v"
    ]
    return run_command(command, "Integration Tests")

def run_performance_tests():
    """Run performance tests"""
    command = [
        "python", "-m", "pytest",
        "fbs_app/tests/",
        "-m", "performance",
        "--benchmark-only",
        "--benchmark-skip",
        "-v"
    ]
    return run_command(command, "Performance Tests")

def run_security_tests():
    """Run security tests"""
    command = [
        "python", "-m", "pytest",
        "fbs_app/tests/",
        "-m", "security",
        "-v"
    ]
    return run_command(command, "Security Tests")

def run_all_tests_with_coverage():
    """Run all tests with coverage reporting"""
    command = [
        "python", "-m", "pytest",
        "fbs_app/tests/",
        "--cov=fbs_app",
        "--cov-report=html",
        "--cov-report=term-missing",
        "--cov-fail-under=90",
        "--tb=short",
        "-v"
    ]
    return run_command(command, "All Tests with Coverage")

def run_specific_test_file(test_file):
    """Run a specific test file"""
    if not os.path.exists(test_file):
        print(f"❌ Test file not found: {test_file}")
        return False
    
    command = [
        "python", "-m", "pytest",
        test_file,
        "--tb=short",
        "-v"
    ]
    return run_command(command, f"Specific Test File: {test_file}")

def run_tests_with_markers(markers):
    """Run tests with specific markers"""
    marker_args = ["-m", " or ".join(markers)]
    command = [
        "python", "-m", "pytest",
        "fbs_app/tests/",
        *marker_args,
        "--tb=short",
        "-v"
    ]
    return run_command(command, f"Tests with markers: {', '.join(markers)}")

def run_parallel_tests():
    """Run tests in parallel for faster execution"""
    command = [
        "python", "-m", "pytest",
        "fbs_app/tests/",
        "-n", "auto",
        "--dist=loadfile",
        "--tb=short",
        "-v"
    ]
    return run_command(command, "Parallel Tests")

def run_benchmark_tests():
    """Run benchmark tests"""
    command = [
        "python", "-m", "pytest",
        "fbs_app/tests/",
        "--benchmark-only",
        "--benchmark-sort=name",
        "-v"
    ]
    return run_command(command, "Benchmark Tests")

def run_linting_and_quality():
    """Run code quality checks"""
    print("\n" + "="*60)
    print("Running Code Quality Checks")
    print("="*60)
    
    # Black formatting check
    black_result = run_command(
        ["python", "-m", "black", "--check", "fbs_app/"],
        "Black Formatting Check"
    )
    
    # Flake8 linting
    flake8_result = run_command(
        ["python", "-m", "flake8", "fbs_app/"],
        "Flake8 Linting"
    )
    
    # Isort import sorting check
    isort_result = run_command(
        ["python", "-m", "isort", "--check-only", "fbs_app/"],
        "Import Sorting Check"
    )
    
    # MyPy type checking
    mypy_result = run_command(
        ["python", "-m", "mypy", "fbs_app/"],
        "MyPy Type Checking"
    )
    
    return all([black_result, flake8_result, isort_result, mypy_result])

def run_security_checks():
    """Run security checks"""
    print("\n" + "="*60)
    print("Running Security Checks")
    print("="*60)
    
    # Bandit security linting
    bandit_result = run_command(
        ["python", "-m", "bandit", "-r", "fbs_app/"],
        "Bandit Security Linting"
    )
    
    # Safety dependency security check
    safety_result = run_command(
        ["python", "-m", "safety", "check"],
        "Dependency Security Check"
    )
    
    return all([bandit_result, safety_result])

def generate_test_report():
    """Generate comprehensive test report"""
    print("\n" + "="*60)
    print("Generating Test Report")
    print("="*60)
    
    # Run tests with coverage and generate reports
    command = [
        "python", "-m", "pytest",
        "fbs_app/tests/",
        "--cov=fbs_app",
        "--cov-report=html:htmlcov",
        "--cov-report=xml:coverage.xml",
        "--cov-report=term-missing",
        "--junitxml=test-results.xml",
        "--tb=short",
        "-v"
    ]
    
    success = run_command(command, "Test Report Generation")
    
    if success:
        print("\n📊 Test reports generated:")
        print("  - HTML coverage: htmlcov/index.html")
        print("  - XML coverage: coverage.xml")
        print("  - JUnit results: test-results.xml")
    
    return success

def main():
    """Main test runner function"""
    parser = argparse.ArgumentParser(description="FBS App Test Runner")
    parser.add_argument(
        "--unit", 
        action="store_true", 
        help="Run unit tests only"
    )
    parser.add_argument(
        "--integration", 
        action="store_true", 
        help="Run integration tests only"
    )
    parser.add_argument(
        "--performance", 
        action="store_true", 
        help="Run performance tests"
    )
    parser.add_argument(
        "--security", 
        action="store_true", 
        help="Run security tests"
    )
    parser.add_argument(
        "--coverage", 
        action="store_true", 
        help="Run all tests with coverage"
    )
    parser.add_argument(
        "--parallel", 
        action="store_true", 
        help="Run tests in parallel"
    )
    parser.add_argument(
        "--benchmark", 
        action="store_true", 
        help="Run benchmark tests"
    )
    parser.add_argument(
        "--quality", 
        action="store_true", 
        help="Run code quality checks"
    )
    parser.add_argument(
        "--security-checks", 
        action="store_true", 
        help="Run security checks"
    )
    parser.add_argument(
        "--report", 
        action="store_true", 
        help="Generate comprehensive test report"
    )
    parser.add_argument(
        "--file", 
        type=str, 
        help="Run specific test file"
    )
    parser.add_argument(
        "--markers", 
        nargs="+", 
        help="Run tests with specific markers"
    )
    parser.add_argument(
        "--all", 
        action="store_true", 
        help="Run all tests and checks"
    )
    
    args = parser.parse_args()
    
    print("🚀 FBS App Test Runner")
    print("="*60)
    
    if args.all:
        print("Running comprehensive test suite...")
        success = True
        
        # Run all tests with coverage
        success &= run_all_tests_with_coverage()
        
        # Run code quality checks
        success &= run_linting_and_quality()
        
        # Run security checks
        success &= run_security_checks()
        
        # Generate report
        success &= generate_test_report()
        
        if success:
            print("\n🎉 All tests and checks completed successfully!")
        else:
            print("\n❌ Some tests or checks failed!")
            sys.exit(1)
    
    elif args.unit:
        run_unit_tests()
    elif args.integration:
        run_integration_tests()
    elif args.performance:
        run_performance_tests()
    elif args.security:
        run_security_tests()
    elif args.coverage:
        run_all_tests_with_coverage()
    elif args.parallel:
        run_parallel_tests()
    elif args.benchmark:
        run_benchmark_tests()
    elif args.quality:
        run_linting_and_quality()
    elif args.security_checks:
        run_security_checks()
    elif args.report:
        generate_test_report()
    elif args.file:
        run_specific_test_file(args.file)
    elif args.markers:
        run_tests_with_markers(args.markers)
    else:
        # Default: run all tests with coverage
        print("No specific option selected, running all tests with coverage...")
        run_all_tests_with_coverage()

if __name__ == "__main__":
    main() 
