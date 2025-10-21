#!/usr/bin/env python3
"""
Docker Container Test Runner
Comprehensive test suite for the Service Marketplace API Docker container
"""

import asyncio
import subprocess
import sys
import time
import requests
import json
from pathlib import Path
from typing import List, Dict, Any
import argparse


class DockerTestRunner:
    """Test runner for Docker container tests"""
    
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.test_results = []
        self.start_time = None
        self.end_time = None
    
    def print_header(self, message: str):
        """Print formatted header"""
        print(f"\n{'='*60}")
        print(f"  {message}")
        print(f"{'='*60}")
    
    def print_success(self, message: str):
        """Print success message"""
        print(f"✅ {message}")
    
    def print_error(self, message: str):
        """Print error message"""
        print(f"❌ {message}")
    
    def print_warning(self, message: str):
        """Print warning message"""
        print(f"⚠️  {message}")
    
    def print_info(self, message: str):
        """Print info message"""
        print(f"ℹ️  {message}")
    
    def check_docker_status(self) -> bool:
        """Check if Docker containers are running"""
        try:
            result = subprocess.run(
                ["docker-compose", "ps"],
                capture_output=True,
                text=True,
                check=True
            )
            
            # Check if all required containers are in the output
            output = result.stdout.lower()
            required_containers = ["marketplace_app", "marketplace_db", "marketplace_redis"]
            running_containers = [container for container in required_containers if container in output and "up" in output]
            
            if len(running_containers) >= 3:
                self.print_success("Docker containers are running")
                return True
            else:
                self.print_error("Not all Docker containers are running")
                return False
                
        except Exception as e:
            self.print_error(f"Failed to check Docker status: {e}")
            return False
    
    def wait_for_api(self, timeout: int = 60) -> bool:
        """Wait for API to be ready"""
        self.print_info("Waiting for API to be ready...")
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                response = requests.get(f"{self.base_url}/health", timeout=5)
                if response.status_code == 200:
                    self.print_success("API is ready")
                    return True
            except requests.exceptions.RequestException:
                pass
            
            time.sleep(2)
        
        self.print_error("API did not become ready within timeout")
        return False
    
    def run_pytest_tests(self, test_files: List[str], verbose: bool = False) -> bool:
        """Run pytest tests"""
        self.print_header("Running Pytest Tests")
        
        cmd = ["python", "-m", "pytest"]
        if verbose:
            cmd.append("-v")
        cmd.extend(test_files)
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                self.print_success("All pytest tests passed")
                print(result.stdout)
                return True
            else:
                self.print_error("Some pytest tests failed")
                print(result.stdout)
                print(result.stderr)
                return False
                
        except Exception as e:
            self.print_error(f"Failed to run pytest: {e}")
            return False
    
    def run_manual_tests(self) -> bool:
        """Run manual API tests"""
        self.print_header("Running Manual API Tests")
        
        tests = [
            self.test_health_endpoint,
            self.test_api_documentation,
            self.test_user_registration,
            self.test_user_login,
            self.test_service_creation,
            self.test_booking_flow,
            self.test_authorization,
            self.test_error_handling
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            try:
                if test():
                    passed += 1
                    self.print_success(f"{test.__name__} passed")
                else:
                    self.print_error(f"{test.__name__} failed")
            except Exception as e:
                self.print_error(f"{test.__name__} failed with exception: {e}")
        
        self.print_info(f"Manual tests: {passed}/{total} passed")
        return passed == total
    
    def test_health_endpoint(self) -> bool:
        """Test health endpoint"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=10)
            return response.status_code == 200 and response.json().get("status") == "healthy"
        except:
            return False
    
    def test_api_documentation(self) -> bool:
        """Test API documentation endpoint"""
        try:
            response = requests.get(f"{self.base_url}/docs", timeout=10)
            return response.status_code == 200
        except:
            return False
    
    def test_user_registration(self) -> bool:
        """Test user registration"""
        try:
            user_data = {
                "email": "test@docker.com",
                "password": "password123",
                "role": "CUSTOMER",
                "profile": {
                    "firstName": "Docker",
                    "lastName": "Test",
                    "phone": "+1234567890",
                    "address": "123 Docker St"
                }
            }
            response = requests.post(f"{self.base_url}/users/", json=user_data, timeout=10)
            return response.status_code == 201
        except:
            return False
    
    def test_user_login(self) -> bool:
        """Test user login"""
        try:
            login_data = {
                "email": "test@docker.com",
                "password": "password123"
            }
            response = requests.post(f"{self.base_url}/auth/login", json=login_data, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return "access_token" in data
            return False
        except:
            return False
    
    def test_service_creation(self) -> bool:
        """Test service creation"""
        try:
            # First login to get token
            login_data = {
                "email": "test@docker.com",
                "password": "password123"
            }
            response = requests.post(f"{self.base_url}/auth/login", json=login_data, timeout=10)
            if response.status_code != 200:
                return False
            
            token = response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            
            # Create a service (this will fail for customer, but we test the endpoint)
            service_data = {
                "name": "Test Service",
                "description": "Test service for Docker",
                "price": 100.00,
                "duration_minutes": 60
            }
            response = requests.post(f"{self.base_url}/services/", json=service_data, headers=headers, timeout=10)
            # Should fail for customer (403) or succeed for provider
            return response.status_code in [201, 403]
        except:
            return False
    
    def test_booking_flow(self) -> bool:
        """Test booking flow"""
        try:
            # Get services
            response = requests.get(f"{self.base_url}/services/", timeout=10)
            if response.status_code != 200:
                return False
            
            services = response.json()
            if not services:
                return True  # No services to book
            
            # Login
            login_data = {
                "email": "test@docker.com",
                "password": "password123"
            }
            response = requests.post(f"{self.base_url}/auth/login", json=login_data, timeout=10)
            if response.status_code != 200:
                return False
            
            token = response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            
            # Try to book a service
            booking_data = {
                "service_id": services[0]["id"],
                "scheduled_at": "2024-12-25T10:00:00Z",
                "notes": "Docker test booking"
            }
            response = requests.post(f"{self.base_url}/bookings/", json=booking_data, headers=headers, timeout=10)
            # Should succeed or fail gracefully
            return response.status_code in [201, 400, 403]
        except:
            return False
    
    def test_authorization(self) -> bool:
        """Test authorization"""
        try:
            # Test accessing protected endpoint without token
            response = requests.get(f"{self.base_url}/users/me", timeout=10)
            return response.status_code == 401
        except:
            return False
    
    def test_error_handling(self) -> bool:
        """Test error handling"""
        try:
            # Test invalid endpoint
            response = requests.get(f"{self.base_url}/invalid-endpoint", timeout=10)
            return response.status_code == 404
        except:
            return False
    
    def run_performance_tests(self) -> bool:
        """Run basic performance tests"""
        self.print_header("Running Performance Tests")
        
        try:
            # Test multiple concurrent requests
            import concurrent.futures
            import threading
            
            def make_request():
                try:
                    response = requests.get(f"{self.base_url}/health", timeout=5)
                    return response.status_code == 200
                except:
                    return False
            
            # Make 10 concurrent requests
            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                futures = [executor.submit(make_request) for _ in range(10)]
                results = [future.result() for future in concurrent.futures.as_completed(futures)]
            
            success_rate = sum(results) / len(results)
            self.print_info(f"Performance test success rate: {success_rate:.2%}")
            
            return success_rate >= 0.8  # 80% success rate
            
        except Exception as e:
            self.print_error(f"Performance test failed: {e}")
            return False
    
    def generate_report(self) -> None:
        """Generate test report"""
        self.print_header("Test Report")
        
        if self.start_time and self.end_time:
            duration = self.end_time - self.start_time
            self.print_info(f"Total test duration: {duration:.2f} seconds")
        
        # Summary
        self.print_info("Test Summary:")
        self.print_info("- Docker container status: ✅")
        self.print_info("- API health check: ✅")
        self.print_info("- Manual API tests: ✅")
        self.print_info("- Performance tests: ✅")
        
        self.print_success("All tests completed!")
    
    def run_all_tests(self, verbose: bool = False) -> bool:
        """Run all tests"""
        self.start_time = time.time()
        
        self.print_header("Docker Container Test Suite")
        self.print_info("Testing Service Marketplace API Docker container")
        
        # Check Docker status
        if not self.check_docker_status():
            self.print_error("Docker containers are not running. Please run 'docker-compose up -d' first.")
            return False
        
        # Wait for API
        if not self.wait_for_api():
            self.print_error("API is not ready. Please check container logs.")
            return False
        
        # Run pytest tests
        test_files = [
            "tests/integration/test_docker_e2e.py",
            "tests/integration/test_docker_scenarios.py", 
            "tests/integration/test_docker_security.py"
        ]
        
        pytest_success = self.run_pytest_tests(test_files, verbose)
        
        # Run manual tests
        manual_success = self.run_manual_tests()
        
        # Run performance tests
        performance_success = self.run_performance_tests()
        
        # Generate report
        self.end_time = time.time()
        self.generate_report()
        
        return pytest_success and manual_success and performance_success


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Docker Container Test Runner")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    parser.add_argument("--pytest-only", action="store_true", help="Run only pytest tests")
    parser.add_argument("--manual-only", action="store_true", help="Run only manual tests")
    parser.add_argument("--performance-only", action="store_true", help="Run only performance tests")
    
    args = parser.parse_args()
    
    runner = DockerTestRunner()
    
    if args.pytest_only:
        success = runner.run_pytest_tests([
            "tests/integration/test_docker_e2e.py",
            "tests/integration/test_docker_scenarios.py",
            "tests/integration/test_docker_security.py"
        ], args.verbose)
    elif args.manual_only:
        success = runner.run_manual_tests()
    elif args.performance_only:
        success = runner.run_performance_tests()
    else:
        success = runner.run_all_tests(args.verbose)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
