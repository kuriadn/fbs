#!/usr/bin/env python
"""
Comprehensive Test Runner for FBS Project

This script provides comprehensive testing across all apps:
- FBS Core App
- License Manager
- Document Management System
- Integration testing
- Cherry-picking scenarios
- Performance and security testing
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path
import time

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def run_command(command, description, timeout=300):
    """Run a command and handle errors with timeout."""
    print(f"\n{'='*80}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(command)}")
    print(f"{'='*80}\n")
    
    try:
        result = subprocess.run(
            command, 
            check=True, 
            capture_output=False,
            timeout=timeout
        )
        print(f"\n✅ {description} completed successfully!")
        return True
    except subprocess.TimeoutExpired:
        print(f"\n⏰ {description} timed out after {timeout} seconds")
        return False
    except subprocess.CalledProcessError as e:
        print(f"\n❌ {description} failed with exit code {e.returncode}")
        return False
    except Exception as e:
        print(f"\n💥 {description} failed with error: {str(e)}")
        return False

def run_unit_tests():
    """Run all unit tests across all apps."""
    command = [
        "python", "-m", "pytest",
        "tests/",
        "-m", "unit",
        "--tb=short",
        "-v",
        "--durations=10"
    ]
    return run_command(command, "Unit Tests (All Apps)")

def run_integration_tests():
    """Run all integration tests across all apps."""
    command = [
        "python", "-m", "pytest",
        "tests/",
        "-m", "integration",
        "--tb=short",
        "-v",
        "--durations=10"
    ]
    return run_command(command, "Integration Tests (All Apps)")

def run_e2e_tests():
    """Run all end-to-end tests."""
    command = [
        "python", "-m", "pytest",
        "tests/",
        "-m", "e2e",
        "--tb=short",
        "-v",
        "--durations=20"
    ]
    return run_command(command, "End-to-End Tests")

def run_cherry_picking_tests():
    """Run cherry-picking scenario tests."""
    command = [
        "python", "-m", "pytest",
        "tests/",
        "-m", "cherry_picking",
        "--tb=short",
        "-v",
        "--durations=10"
    ]
    return run_command(command, "Cherry-Picking Tests")

def run_isolation_tests():
    """Run database isolation architecture tests."""
    command = [
        "python", "-m", "pytest",
        "tests/",
        "-m", "isolation",
        "--tb=short",
        "-v",
        "--durations=10"
    ]
    return run_command(command, "Isolation Architecture Tests")

def run_performance_tests():
    """Run performance tests."""
    command = [
        "python", "-m", "pytest",
        "tests/",
        "-m", "performance",
        "--tb=short",
        "-v",
        "--durations=20"
    ]
    return run_command(command, "Performance Tests")

def run_security_tests():
    """Run security tests."""
    command = [
        "python", "-m", "pytest",
        "tests/",
        "-m", "security",
        "--tb=short",
        "-v",
        "--durations=10"
    ]
    return run_command(command, "Security Tests")

def run_app_specific_tests(app_name):
    """Run tests for a specific app."""
    command = [
        "python", "-m", "pytest",
        f"tests/test_{app_name}_*.py",
        "--tb=short",
        "-v",
        "--durations=10"
    ]
    return run_command(command, f"{app_name.title()} App Tests")

def run_all_tests_with_coverage():
    """Run all tests with comprehensive coverage reporting."""
    command = [
        "python", "-m", "pytest",
        "tests/",
        "--cov=fbs_app",
        "--cov=fbs_license_manager",
        "--cov=fbs_dms",
        "--cov-report=html",
        "--cov-report=term-missing",
        "--cov-report=xml",
        "--cov-fail-under=80",
        "--tb=short",
        "-v",
        "--durations=20"
    ]
    return run_command(command, "All Tests with Coverage", timeout=600)

def run_specific_test_file(test_file):
    """Run a specific test file."""
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

def run_test_category(category):
    """Run tests for a specific category."""
    categories = {
        'fbs_app': run_app_specific_tests('fbs_app'),
        'license_manager': run_app_specific_tests('license_manager'),
        'dms': run_app_specific_tests('dms'),
        'unit': run_unit_tests(),
        'integration': run_integration_tests(),
        'e2e': run_e2e_tests(),
        'cherry_picking': run_cherry_picking_tests(),
        'isolation': run_isolation_tests(),
        'performance': run_performance_tests(),
        'security': run_security_tests(),
        'coverage': run_all_tests_with_coverage()
    }
    
    if category in categories:
        return categories[category]
    else:
        print(f"❌ Unknown test category: {category}")
        print(f"Available categories: {', '.join(categories.keys())}")
        return False

def run_test_suite(suite_name):
    """Run a specific test suite."""
    suites = {
        'models': run_command([
            "python", "-m", "pytest",
            "tests/test_*_models.py",
            "--tb=short",
            "-v"
        ], "Model Tests"),
        
        'services': run_command([
            "python", "-m", "pytest",
            "tests/test_*_services.py",
            "--tb=short",
            "-v"
        ], "Service Tests"),
        
        'views': run_command([
            "python", "-m", "pytest",
            "tests/test_*_views.py",
            "--tb=short",
            "-v"
        ], "View Tests"),
        
        'admin': run_command([
            "python", "-m", "pytest",
            "tests/test_*_admin.py",
            "--tb=short",
            "-v"
        ], "Admin Tests"),
        
        'integration': run_command([
            "python", "-m", "pytest",
            "tests/test_*_integration.py",
            "--tb=short",
            "-v"
        ], "Integration Tests")
    }
    
    if suite_name in suites:
        return suites[suite_name]
    else:
        print(f"❌ Unknown test suite: {suite_name}")
        print(f"Available suites: {', '.join(suites.keys())}")
        return False

def run_comprehensive_test_suite():
    """Run the complete comprehensive test suite."""
    print("🚀 Starting Comprehensive Test Suite for FBS Project")
    print("=" * 80)
    
    start_time = time.time()
    results = {}
    
    # 1. Unit Tests
    print("\n📋 Phase 1: Unit Tests")
    results['unit_tests'] = run_unit_tests()
    
    # 2. Integration Tests
    print("\n📋 Phase 2: Integration Tests")
    results['integration_tests'] = run_integration_tests()
    
    # 3. App-Specific Tests
    print("\n📋 Phase 3: App-Specific Tests")
    results['fbs_app_tests'] = run_app_specific_tests('fbs_app')
    results['license_manager_tests'] = run_app_specific_tests('license_manager')
    results['dms_tests'] = run_app_specific_tests('dms')
    
    # 4. Cherry-Picking Tests
    print("\n📋 Phase 4: Cherry-Picking Tests")
    results['cherry_picking_tests'] = run_cherry_picking_tests()
    
    # 5. Isolation Tests
    print("\n📋 Phase 5: Isolation Architecture Tests")
    results['isolation_tests'] = run_isolation_tests()
    
    # 6. Performance Tests
    print("\n📋 Phase 6: Performance Tests")
    results['performance_tests'] = run_performance_tests()
    
    # 7. Security Tests
    print("\n📋 Phase 7: Security Tests")
    results['security_tests'] = run_security_tests()
    
    # 8. End-to-End Tests
    print("\n📋 Phase 8: End-to-End Tests")
    results['e2e_tests'] = run_e2e_tests()
    
    # 9. Coverage Report
    print("\n📋 Phase 9: Coverage Report")
    results['coverage_tests'] = run_all_tests_with_coverage()
    
    end_time = time.time()
    total_duration = end_time - start_time
    
    # Print results summary
    print("\n" + "=" * 80)
    print("📊 COMPREHENSIVE TEST SUITE RESULTS")
    print("=" * 80)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name.replace('_', ' ').title()}: {status}")
    
    print(f"\n⏱️  Total Duration: {total_duration:.2f} seconds")
    
    # Calculate overall success rate
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    success_rate = (passed / total) * 100
    
    print(f"📈 Success Rate: {passed}/{total} ({success_rate:.1f}%)")
    
    if success_rate >= 90:
        print("🎉 EXCELLENT! Test suite passed with high success rate!")
    elif success_rate >= 80:
        print("👍 GOOD! Test suite passed with good success rate.")
    elif success_rate >= 70:
        print("⚠️  FAIR! Test suite passed with acceptable success rate.")
    else:
        print("❌ POOR! Test suite needs attention.")
    
    return success_rate >= 80

def main():
    """Main function to handle command line arguments."""
    parser = argparse.ArgumentParser(
        description="Comprehensive Test Runner for FBS Project"
    )
    
    parser.add_argument(
        '--category',
        choices=[
            'fbs_app', 'license_manager', 'dms',
            'unit', 'integration', 'e2e', 'cherry_picking',
            'isolation', 'performance', 'security', 'coverage'
        ],
        help='Run tests for a specific category'
    )
    
    parser.add_argument(
        '--suite',
        choices=['models', 'services', 'views', 'admin', 'integration'],
        help='Run tests for a specific suite'
    )
    
    parser.add_argument(
        '--file',
        help='Run a specific test file'
    )
    
    parser.add_argument(
        '--comprehensive',
        action='store_true',
        help='Run the complete comprehensive test suite'
    )
    
    parser.add_argument(
        '--list',
        action='store_true',
        help='List available test categories and suites'
    )
    
    args = parser.parse_args()
    
    if args.list:
        print("📋 Available Test Categories:")
        print("  - fbs_app: FBS Core App tests")
        print("  - license_manager: License Manager tests")
        print("  - dms: Document Management System tests")
        print("  - unit: All unit tests")
        print("  - integration: All integration tests")
        print("  - e2e: All end-to-end tests")
        print("  - cherry_picking: Cherry-picking scenario tests")
        print("  - isolation: Database isolation tests")
        print("  - performance: Performance tests")
        print("  - security: Security tests")
        print("  - coverage: All tests with coverage")
        
        print("\n📋 Available Test Suites:")
        print("  - models: Model tests")
        print("  - services: Service tests")
        print("  - views: View tests")
        print("  - admin: Admin interface tests")
        print("  - integration: Integration tests")
        
        print("\n📋 Usage Examples:")
        print("  python tests/run_comprehensive_tests.py --comprehensive")
        print("  python tests/run_comprehensive_tests.py --category fbs_app")
        print("  python tests/run_comprehensive_tests.py --suite models")
        print("  python tests/run_comprehensive_tests.py --file tests/test_fbs_app_models.py")
        
        return
    
    if args.comprehensive:
        success = run_comprehensive_test_suite()
        sys.exit(0 if success else 1)
    
    if args.category:
        success = run_test_category(args.category)
        sys.exit(0 if success else 1)
    
    if args.suite:
        success = run_test_suite(args.suite)
        sys.exit(0 if success else 1)
    
    if args.file:
        success = run_specific_test_file(args.file)
        sys.exit(0 if success else 1)
    
    # Default: run comprehensive test suite
    print("No specific test specified. Running comprehensive test suite...")
    success = run_comprehensive_test_suite()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
