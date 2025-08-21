#!/usr/bin/env python3
"""
Comprehensive Test Runner for FBS App

This script runs all tests for the FBS app including:
- Model tests
- Service tests (newly created)
- Interface tests
- Performance and integration tests

Usage:
    python run_all_tests.py [--verbose] [--coverage] [--performance]
"""

import os
import sys
import time
import argparse
import subprocess
from pathlib import Path

def run_command(command, description):
    """Run a command and return success status"""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {command}")
    print(f"{'='*60}")
    
    start_time = time.time()
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        end_time = time.time()
        duration = end_time - start_time
        
        if result.returncode == 0:
            print(f"✅ SUCCESS: {description}")
            print(f"⏱️  Duration: {duration:.2f} seconds")
            if result.stdout:
                print("Output:")
                print(result.stdout)
            return True
        else:
            print(f"❌ FAILED: {description}")
            print(f"⏱️  Duration: {duration:.2f} seconds")
            print(f"Return code: {result.returncode}")
            if result.stderr:
                print("Error output:")
                print(result.stderr)
            if result.stdout:
                print("Standard output:")
                print(result.stdout)
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {description}")
        print(f"Exception: {str(e)}")
        return False

def run_django_check():
    """Run Django system check"""
    return run_command(
        "cd .. && PYTHONPATH=. python fbs_project/manage.py check",
        "Django System Check"
    )

def run_model_tests():
    """Run model tests"""
    return run_command(
        "cd .. && PYTHONPATH=. python fbs_project/manage.py test fbs_app.tests.test_models -v 2",
        "Model Tests"
    )

def run_bi_service_tests():
    """Run Business Intelligence service tests"""
    return run_command(
        "cd .. && PYTHONPATH=. python fbs_project/manage.py test fbs_app.tests.test_bi_service -v 2",
        "Business Intelligence Service Tests"
    )

def run_workflow_service_tests():
    """Run Workflow service tests"""
    return run_command(
        "cd .. && PYTHONPATH=. python fbs_project/manage.py test fbs_app.tests.test_workflow_service -v 2",
        "Workflow Service Tests"
    )

def run_compliance_service_tests():
    """Run Compliance service tests"""
    return run_command(
        "cd .. && PYTHONPATH=. python fbs_project/manage.py test fbs_app.tests.test_compliance_service -v 2",
        "Compliance Service Tests"
    )

def run_notification_service_tests():
    """Run Notification service tests"""
    return run_command(
        "cd .. && PYTHONPATH=. python fbs_project/manage.py test fbs_app.tests.test_notification_service -v 2",
        "Notification Service Tests"
    )

def run_onboarding_service_tests():
    """Run Onboarding service tests"""
    return run_command(
        "cd .. && PYTHONPATH=. python fbs_project/manage.py test fbs_app.tests.test_onboarding_service -v 2",
        "Onboarding Service Tests"
    )

def run_interface_tests():
    """Run interface tests"""
    return run_command(
        "cd .. && PYTHONPATH=. python fbs_project/manage.py test fbs_app.tests.test_interfaces -v 2",
        "Interface Tests"
    )

def run_all_tests():
    """Run all tests"""
    return run_command(
        "cd .. && PYTHONPATH=. python fbs_project/manage.py test fbs_app.tests -v 2",
        "All FBS App Tests"
    )

def run_coverage_tests():
    """Run tests with coverage reporting"""
    return run_command(
        "cd .. && PYTHONPATH=. python fbs_project/manage.py test fbs_app.tests --coverage",
        "Tests with Coverage"
    )

def run_performance_tests():
    """Run performance-focused tests"""
    return run_command(
        "cd .. && PYTHONPATH=. python fbs_project/manage.py test fbs_app.tests.test_models.TestModelPerformance -v 2",
        "Performance Tests"
    )

def generate_test_report(results):
    """Generate a comprehensive test report"""
    print(f"\n{'='*80}")
    print("FBS APP TEST EXECUTION REPORT")
    print(f"{'='*80}")
    
    total_tests = len(results)
    passed_tests = sum(1 for result in results.values() if result)
    failed_tests = total_tests - passed_tests
    
    print(f"\n📊 SUMMARY:")
    print(f"   Total Tests: {total_tests}")
    print(f"   ✅ Passed: {passed_tests}")
    print(f"   ❌ Failed: {failed_tests}")
    print(f"   📈 Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    print(f"\n📋 DETAILED RESULTS:")
    for test_name, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"   {status} {test_name}")
    
    if failed_tests > 0:
        print(f"\n🚨 FAILED TESTS:")
        for test_name, success in results.items():
            if not success:
                print(f"   ❌ {test_name}")
    
    print(f"\n{'='*80}")
    
    if failed_tests == 0:
        print("🎉 ALL TESTS PASSED! The FBS app is working correctly.")
    else:
        print(f"⚠️  {failed_tests} test(s) failed. Please review the errors above.")
    
    return failed_tests == 0

def main():
    """Main test runner function"""
    parser = argparse.ArgumentParser(description="FBS App Test Runner")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--coverage", "-c", action="store_true", help="Run with coverage")
    parser.add_argument("--performance", "-p", action="store_true", help="Run performance tests")
    parser.add_argument("--quick", "-q", action="store_true", help="Quick test run (models only)")
    parser.add_argument("--services", "-s", action="store_true", help="Run service tests only")
    
    args = parser.parse_args()
    
    print("🚀 FBS App Test Runner")
    print("=" * 60)
    
    # Determine which tests to run
    if args.quick:
        test_functions = [
            ("Django Check", run_django_check),
            ("Model Tests", run_model_tests),
        ]
    elif args.services:
        test_functions = [
            ("Django Check", run_django_check),
            ("BI Service Tests", run_bi_service_tests),
            ("Workflow Service Tests", run_workflow_service_tests),
            ("Compliance Service Tests", run_compliance_service_tests),
            ("Notification Service Tests", run_notification_service_tests),
            ("Onboarding Service Tests", run_onboarding_service_tests),
        ]
    else:
        test_functions = [
            ("Django Check", run_django_check),
            ("Model Tests", run_model_tests),
            ("BI Service Tests", run_bi_service_tests),
            ("Workflow Service Tests", run_workflow_service_tests),
            ("Compliance Service Tests", run_compliance_service_tests),
            ("Notification Service Tests", run_notification_service_tests),
            ("Onboarding Service Tests", run_onboarding_service_tests),
            ("Interface Tests", run_interface_tests),
        ]
    
    if args.performance:
        test_functions.append(("Performance Tests", run_performance_tests))
    
    if args.coverage:
        test_functions.append(("Coverage Tests", run_coverage_tests))
    
    # Run tests
    results = {}
    start_time = time.time()
    
    for test_name, test_func in test_functions:
        results[test_name] = test_func()
    
    end_time = time.time()
    total_duration = end_time - start_time
    
    # Generate report
    all_passed = generate_test_report(results)
    
    print(f"\n⏱️  Total Execution Time: {total_duration:.2f} seconds")
    
    # Exit with appropriate code
    sys.exit(0 if all_passed else 1)

if __name__ == "__main__":
    main()
