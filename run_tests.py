import subprocess
import os
import sys

def run_command(command, cwd=None):
    """Runs a shell command and returns its output and exit code."""
    print(f"Running command: {command}")
    process = subprocess.run(command, shell=True, capture_output=True, text=True, cwd=cwd)
    if process.stdout:
        print("Command Output:")
        print(process.stdout)
    if process.stderr:
        print("Command Error Output:")
        print(process.stderr)
    return process.returncode, process.stdout, process.stderr

def main():
    print("============================================================")
    print("🚀 Starting Comprehensive Test Suite for Service Marketplace API")
    print("============================================================")

    # Ensure virtual environment is activated
    if "VIRTUAL_ENV" not in os.environ:
        print("Activating virtual environment...")
        # This might not work directly if the script is run in a new shell.
        # For robust activation, the user should activate it manually before running the script.
        # For now, we'll assume it's activated or try a common path.
        venv_activate = os.path.join(os.getcwd(), "venv", "bin", "activate")
        if os.path.exists(venv_activate):
            # This will only activate for the subprocess, not the parent shell
            os.environ["PATH"] = os.path.join(os.getcwd(), "venv", "bin") + os.pathsep + os.environ["PATH"]
            print("Virtual environment path added to PATH.")
        else:
            print("Warning: Virtual environment 'venv' not found or not activated. Tests might fail due to missing dependencies.")
            print("Please activate your virtual environment manually: source venv/bin/activate")
            # sys.exit(1) # Don't exit, let pytest try to run anyway

    # Install dependencies
    print("\n📦 Installing/Updating test dependencies...")
    install_deps_cmd = "pip install -r requirements.txt"
    return_code, _, stderr = run_command(install_deps_cmd)
    if return_code != 0:
        print(f"❌ Failed to install dependencies. Error: {stderr}")
        sys.exit(1)
    print("✅ Dependencies installed.")

    # Run unit tests
    print("\n🔬 Running Unit Tests...")
    unit_test_cmd = "python -m pytest tests/unit/ -v"
    return_code, stdout, stderr = run_command(unit_test_cmd)
    if return_code == 0:
        print("✅ Unit Tests: PASSED")
    else:
        print("❌ Unit Tests: FAILED")
        print(stderr) # Print stderr for failures
        # sys.exit(1) # Don't exit, continue to integration tests

    # Run integration tests
    print("\n🔗 Running Integration Tests...")
    integration_test_cmd = "python -m pytest tests/integration/ -v"
    return_code, stdout, stderr = run_command(integration_test_cmd)
    if return_code == 0:
        print("✅ Integration Tests: PASSED")
    else:
        print("❌ Integration Tests: FAILED")
        print(stderr) # Print stderr for failures
        # sys.exit(1) # Don't exit, continue to coverage

    # Run all tests with coverage
    print("\n📊 Running All Tests with Coverage...")
    # The --cov-exclude options are now handled in pytest.ini
    coverage_cmd = "python -m pytest tests/ --cov=. --cov-report=html --cov-report=term-missing"
    return_code, stdout, stderr = run_command(coverage_cmd)
    if return_code == 0:
        print("✅ Coverage Report: GENERATED")
        print("   View HTML report at: htmlcov/index.html")
    else:
        print("❌ Coverage Report: FAILED")
        print(stderr) # Print stderr for failures

    print("\n============================================================")
    print("📋 TEST SUMMARY")
    print("============================================================")
    if return_code == 0:
        print("✅ ALL TESTS PASSED!")
    else:
        print("💥 SOME TESTS FAILED!")

if __name__ == "__main__":
    main()
