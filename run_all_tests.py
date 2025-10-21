#!/usr/bin/env python3
"""
Master test runner for the Service Marketplace API
Runs all unit and integration tests with detailed reporting
"""
import os
import sys
import subprocess
from pathlib import Path


def print_banner(text):
    """Print a formatted banner"""
    width = 80
    print("\n" + "=" * width)
    print(f"{text.center(width)}")
    print("=" * width + "\n")


def run_tests():
    """Run all tests with pytest"""
    print_banner("SERVICE MARKETPLACE API - TEST SUITE")
    
    # Ensure we're in the project root
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    # Set environment variables for testing
    os.environ["TESTING"] = "1"
    os.environ["PAYMENT_FAILURE_RATE"] = "0.0"
    
    print("📋 Test Configuration:")
    print(f"   Project Root: {project_root}")
    print(f"   Python: {sys.version.split()[0]}")
    print(f"   Testing Mode: Enabled")
    print(f"   Payment Failure Rate: 0% (for consistent tests)")
    print()
    
    # Check if pytest is installed
    try:
        import pytest
    except ImportError:
        print("❌ pytest is not installed!")
        print("   Install with: pip install pytest pytest-asyncio")
        return 1
    
    # Test categories
    test_categories = [
        {
            "name": "Unit Tests - Authentication",
            "path": "tests/unit/test_authentication.py",
            "description": "JWT token generation, validation, login/logout"
        },
        {
            "name": "Unit Tests - Authorization",
            "path": "tests/unit/test_authorization.py",
            "description": "Role-based access control, ownership permissions"
        },
        {
            "name": "Unit Tests - Booking Flow",
            "path": "tests/unit/test_booking_flow.py",
            "description": "Complete booking workflow with payment processing"
        },
        {
            "name": "Integration Tests - Complete API",
            "path": "tests/integration/test_api_complete.py",
            "description": "End-to-end API flows, user journeys"
        }
    ]
    
    results = []
    
    # Run each test category
    for category in test_categories:
        print_banner(category["name"])
        print(f"📝 {category['description']}")
        print()
        
        if not Path(category["path"]).exists():
            print(f"⚠️  Test file not found: {category['path']}")
            results.append({"name": category["name"], "status": "SKIPPED", "exit_code": -1})
            continue
        
        # Run pytest for this category
        cmd = [
            sys.executable, "-m", "pytest",
            category["path"],
            "-v",  # Verbose
            "--tb=short",  # Short traceback format
            "--color=yes",  # Colored output
            "-W", "ignore::DeprecationWarning"  # Ignore deprecation warnings
        ]
        
        result = subprocess.run(cmd, capture_output=False)
        
        if result.returncode == 0:
            print(f"\n✅ {category['name']} - PASSED")
            results.append({"name": category["name"], "status": "PASSED", "exit_code": 0})
        else:
            print(f"\n❌ {category['name']} - FAILED")
            results.append({"name": category["name"], "status": "FAILED", "exit_code": result.returncode})
    
    # Print summary
    print_banner("TEST SUMMARY")
    
    passed = sum(1 for r in results if r["status"] == "PASSED")
    failed = sum(1 for r in results if r["status"] == "FAILED")
    skipped = sum(1 for r in results if r["status"] == "SKIPPED")
    total = len(results)
    
    for result in results:
        status_icon = "✅" if result["status"] == "PASSED" else "❌" if result["status"] == "FAILED" else "⚠️"
        print(f"{status_icon} {result['name']}: {result['status']}")
    
    print()
    print(f"Total: {total} | Passed: {passed} | Failed: {failed} | Skipped: {skipped}")
    
    if failed == 0 and skipped == 0:
        print("\n🎉 ALL TESTS PASSED! 🎉")
        return 0
    elif failed == 0:
        print(f"\n⚠️  All tests passed but {skipped} skipped")
        return 0
    else:
        print(f"\n❌ {failed} test category(ies) failed")
        return 1


def run_quick_tests():
    """Run tests in quick mode (less verbose)"""
    print_banner("QUICK TEST MODE")
    
    os.environ["TESTING"] = "1"
    os.environ["PAYMENT_FAILURE_RATE"] = "0.0"
    
    cmd = [
        sys.executable, "-m", "pytest",
        "tests/",
        "-q",  # Quiet mode
        "--tb=line",  # One line traceback
        "-W", "ignore::DeprecationWarning"
    ]
    
    result = subprocess.run(cmd)
    return result.returncode


def run_coverage():
    """Run tests with coverage report"""
    print_banner("TEST COVERAGE REPORT")
    
    os.environ["TESTING"] = "1"
    os.environ["PAYMENT_FAILURE_RATE"] = "0.0"
    
    try:
        import pytest_cov
    except ImportError:
        print("❌ pytest-cov is not installed!")
        print("   Install with: pip install pytest-cov")
        return 1
    
    cmd = [
        sys.executable, "-m", "pytest",
        "tests/",
        "--cov=.",
        "--cov-report=term-missing",
        "--cov-report=html",
        "-W", "ignore::DeprecationWarning"
    ]
    
    result = subprocess.run(cmd)
    
    if result.returncode == 0:
        print("\n📊 Coverage report generated in htmlcov/index.html")
    
    return result.returncode


def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        mode = sys.argv[1]
        
        if mode == "--quick" or mode == "-q":
            return run_quick_tests()
        elif mode == "--coverage" or mode == "-c":
            return run_coverage()
        elif mode == "--help" or mode == "-h":
            print("Usage: python run_all_tests.py [options]")
            print()
            print("Options:")
            print("  (none)          Run all tests with detailed output")
            print("  --quick, -q     Run all tests in quick mode")
            print("  --coverage, -c  Run tests with coverage report")
            print("  --help, -h      Show this help message")
            return 0
        else:
            print(f"Unknown option: {mode}")
            print("Use --help for available options")
            return 1
    
    return run_tests()


if __name__ == "__main__":
    sys.exit(main())

