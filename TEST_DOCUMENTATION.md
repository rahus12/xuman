# Test Documentation

## Overview
This document describes the comprehensive test suite for the Service Marketplace API. The tests are organized using pytest and cover unit tests, integration tests, and end-to-end API testing.

## Test Structure

```
tests/
├── __init__.py
├── conftest.py
├── unit/
│   ├── test_authentication.py
│   ├── test_booking_management.py
│   ├── test_email_notifications.py
│   ├── test_password_reset.py
│   ├── test_service_management.py
│   └── test_user_management.py
├── integration/
│   └── test_api_endpoints.py
└── fixtures/
    └── sample_data.py
```

## Test Configuration

### pytest.ini
```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts =
    --verbose
    --tb=short
    --cov=.
    --cov-report=html
    --cov-report=term-missing
    --cov-omit=tests/*
    --cov-omit=venv/*
    --cov-omit=email_notifications/*
asyncio_mode = auto
```

### Test Database
- Uses in-memory SQLite for testing
- Fresh database for each test function
- Tables created and dropped automatically
- No data persistence between tests

## Test Categories

### 1. Unit Tests
Test individual components in isolation with mocked dependencies.

#### Authentication Tests (`test_authentication.py`)
- Password hashing and verification
- JWT token generation and validation
- Authentication dependencies
- Role-based access control

**Key Test Cases:**
- `test_get_password_hash()` - Password hashing
- `test_verify_password_correct()` - Password verification
- `test_create_access_token_default_expiry()` - Token generation
- `test_get_current_user_success()` - User authentication
- `test_get_current_user_invalid_token()` - Invalid token handling

#### User Management Tests (`test_user_management.py`)
- User creation and validation
- User retrieval by email
- User listing with role filtering
- Password verification

**Key Test Cases:**
- `test_create_user_success()` - Successful user creation
- `test_create_user_duplicate_email()` - Duplicate email handling
- `test_get_user_by_email_success()` - User retrieval
- `test_list_users_by_role()` - Role-based filtering
- `test_verify_user_password_success()` - Password verification

#### Service Management Tests (`test_service_management.py`)
- Service CRUD operations
- Service validation
- Error handling

**Key Test Cases:**
- `test_create_service_success()` - Service creation
- `test_get_service_success()` - Service retrieval
- `test_update_service_success()` - Service updates
- `test_delete_service_success()` - Service deletion
- `test_list_services()` - Service listing

#### Booking Management Tests (`test_booking_management.py`)
- Booking creation and validation
- Booking status updates
- Booking retrieval and listing
- Email notification integration

**Key Test Cases:**
- `test_create_booking_success()` - Booking creation
- `test_update_booking_success()` - Booking updates
- `test_list_bookings_with_filters()` - Filtered listing
- `test_delete_booking_success()` - Booking deletion

#### Password Reset Tests (`test_password_reset.py`)
- Password reset token generation
- Token validation and expiration
- Password reset flow
- Email notification

**Key Test Cases:**
- `test_request_password_reset_success()` - Reset request
- `test_confirm_password_reset_success()` - Reset confirmation
- `test_reset_token_expiration()` - Token expiration
- `test_reset_token_single_use()` - Single-use tokens

#### Email Notification Tests (`test_email_notifications.py`)
- Email template generation
- File-based email storage
- Email content validation

**Key Test Cases:**
- `test_send_booking_confirmation()` - Booking emails
- `test_send_password_reset_email()` - Reset emails
- `test_email_file_creation()` - File storage
- `test_email_content_validation()` - Content validation

### 2. Integration Tests
Test API endpoints with real database interactions.

#### API Endpoint Tests (`test_api_endpoints.py`)
- Complete API workflow testing
- Authentication flow
- CRUD operations via HTTP
- Error handling and status codes

**Key Test Cases:**
- `test_user_registration_flow()` - User registration
- `test_user_login_flow()` - Authentication
- `test_service_creation_flow()` - Service management
- `test_booking_creation_flow()` - Booking workflow
- `test_password_reset_flow()` - Password reset

## Test Fixtures

### Database Fixtures
```python
@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test."""
    # Creates in-memory SQLite database
    # Sets up all required tables
    # Yields session for test use
    # Cleans up after test completion
```

### Sample Data Fixtures
```python
@pytest.fixture
def sample_customer():
    """Sample customer user for testing."""
    
@pytest.fixture
def sample_provider():
    """Sample provider user for testing."""
    
@pytest.fixture
def sample_service():
    """Sample service for testing."""
    
@pytest.fixture
def sample_booking():
    """Sample booking for testing."""
```

### Test Client Fixture
```python
@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with database dependency override."""
    # Overrides database dependency
    # Provides FastAPI test client
    # Cleans up after test completion
```

## Test Data Management

### Sample Data Structure
- **Users**: Customer and provider profiles
- **Services**: Various service categories and pricing
- **Bookings**: Different statuses and time slots
- **Tokens**: Password reset tokens with expiration

### Data Isolation
- Each test gets fresh database
- No data sharing between tests
- Automatic cleanup after each test
- Consistent test environment

## Mocking Strategy

### External Dependencies
- **Email Service**: Mocked to prevent actual email sending
- **Password Hashing**: Mocked for consistent test results
- **Database Errors**: Simulated for error handling tests

### Mock Examples
```python
with patch('services.users_service.get_password_hash', return_value="hashed_password"):
    # Test password hashing without actual bcrypt
    
with patch('services.email_service.EmailService.send_email') as mock_send:
    # Test email functionality without sending emails
```

## Test Coverage

### Coverage Goals
- **Unit Tests**: 90%+ coverage for business logic
- **Integration Tests**: 80%+ coverage for API endpoints
- **Error Handling**: 100% coverage for error scenarios

### Coverage Exclusions
- Test files themselves
- Virtual environment files
- Email notification files
- Database migration files

### Coverage Reports
- **Terminal**: Real-time coverage during test runs
- **HTML**: Detailed coverage report in `htmlcov/index.html`
- **Missing Lines**: Identifies untested code paths

## Running Tests

### Individual Test Files
```bash
# Run specific test file
python -m pytest tests/unit/test_user_management.py -v

# Run specific test class
python -m pytest tests/unit/test_user_management.py::TestUserService -v

# Run specific test method
python -m pytest tests/unit/test_user_management.py::TestUserService::test_create_user_success -v
```

### Test Categories
```bash
# Run all unit tests
python -m pytest tests/unit/ -v

# Run all integration tests
python -m pytest tests/integration/ -v

# Run all tests
python -m pytest tests/ -v
```

### Coverage Reports
```bash
# Run tests with coverage
python -m pytest tests/ --cov=. --cov-report=html --cov-report=term-missing

# View HTML coverage report
open htmlcov/index.html
```

### Test Script
```bash
# Run comprehensive test suite
python run_tests.py
```

## Test Best Practices

### 1. Test Naming
- Use descriptive test names
- Follow pattern: `test_<action>_<scenario>_<expected_result>`
- Examples:
  - `test_create_user_success()`
  - `test_create_user_duplicate_email()`
  - `test_get_user_by_email_not_found()`

### 2. Test Structure
- **Arrange**: Set up test data and mocks
- **Act**: Execute the code under test
- **Assert**: Verify expected outcomes

### 3. Test Isolation
- Each test is independent
- No shared state between tests
- Clean up after each test

### 4. Error Testing
- Test both success and failure scenarios
- Verify error messages and status codes
- Test edge cases and boundary conditions

### 5. Mock Usage
- Mock external dependencies
- Mock expensive operations
- Verify mock interactions when relevant

## Continuous Integration

### GitHub Actions (Recommended)
```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.14
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: python -m pytest tests/ --cov=. --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v1
```

### Local Development
```bash
# Run tests before committing
python -m pytest tests/ -v

# Run tests with coverage
python -m pytest tests/ --cov=. --cov-report=html

# Run specific test category
python -m pytest tests/unit/ -v
```

## Debugging Tests

### Verbose Output
```bash
# Show detailed test output
python -m pytest tests/ -v -s

# Show print statements
python -m pytest tests/ -s

# Show local variables on failure
python -m pytest tests/ --tb=long
```

### Test Debugging
```python
# Add breakpoints in tests
import pdb; pdb.set_trace()

# Use pytest debugging
pytest --pdb

# Run specific failing test
pytest tests/unit/test_user_management.py::TestUserService::test_create_user_success -v -s
```

## Performance Testing

### Load Testing (Future)
- API endpoint performance
- Database query optimization
- Concurrent user simulation
- Memory usage monitoring

### Test Performance
- Test execution time
- Database setup/teardown time
- Mock overhead analysis

## Maintenance

### Regular Updates
- Update test data as models change
- Add tests for new features
- Remove obsolete tests
- Update test documentation

### Test Quality
- Review test coverage regularly
- Refactor duplicate test code
- Improve test readability
- Add missing edge cases

## Troubleshooting

### Common Issues

#### Database Connection Errors
```bash
# Ensure PostgreSQL is running
brew services start postgresql@14

# Check database URL
echo $DATABASE_URL
```

#### Import Errors
```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### Test Failures
```bash
# Run with verbose output
python -m pytest tests/ -v -s

# Check specific test
python -m pytest tests/unit/test_user_management.py::TestUserService::test_create_user_success -v -s
```

### Test Environment
- Python 3.14+
- pytest 7.4.3+
- pytest-asyncio 0.21.1+
- httpx 0.25.2+
- pytest-cov 4.1.0+
