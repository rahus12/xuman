#!/bin/bash

# Service Marketplace API Setup Script
# This script automates the setup process for different environments

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check Python version
check_python() {
    if command_exists python3; then
        PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
        if [[ $(echo "$PYTHON_VERSION >= 3.8" | bc -l) -eq 1 ]]; then
            print_status "Python $PYTHON_VERSION found"
            return 0
        else
            print_error "Python 3.8+ required, found $PYTHON_VERSION"
            return 1
        fi
    else
        print_error "Python 3 not found"
        return 1
    fi
}

# Function to check PostgreSQL
check_postgresql() {
    if command_exists psql; then
        print_status "PostgreSQL found"
        return 0
    else
        print_warning "PostgreSQL not found. Please install PostgreSQL first."
        print_info "Installation instructions:"
        print_info "  macOS: brew install postgresql"
        print_info "  Ubuntu: sudo apt-get install postgresql"
        print_info "  CentOS: sudo yum install postgresql-server"
        return 1
    fi
}

# Function to create virtual environment
create_venv() {
    if [ ! -d "venv" ]; then
        print_info "Creating virtual environment..."
        python3 -m venv venv
        print_status "Virtual environment created"
    else
        print_status "Virtual environment already exists"
    fi
}

# Function to activate virtual environment
activate_venv() {
    print_info "Activating virtual environment..."
    source venv/bin/activate
    print_status "Virtual environment activated"
}

# Function to install dependencies
install_dependencies() {
    print_info "Installing Python dependencies..."
    pip install --upgrade pip
    pip install -r requirements.txt
    print_status "Dependencies installed"
}

# Function to setup environment
setup_environment() {
    print_info "Setting up environment..."
    
    if [ -f ".env" ]; then
        print_status "Environment file already exists"
        print_info "Please update .env with your actual configuration if needed"
    else
        if [ -f "env.template" ]; then
            cp env.template .env
            print_status "Environment template copied to .env"
            print_warning "Please update .env with your actual configuration"
        else
            print_error "No .env file or env.template found"
            print_info "Please create a .env file with your configuration"
            print_info "Required variables:"
            echo ""
            echo "DATABASE_URL=postgresql+psycopg://username:password@localhost:5432/service_marketplace"
            echo "JWT_SECRET_KEY=your-secret-key"
            echo "JWT_ALGORITHM=HS256"
            echo "JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30"
            echo "DEBUG=true"
            echo "HOST=0.0.0.0"
            echo "PORT=8000"
            echo ""
            return 1
        fi
    fi
}

# Function to setup database
setup_database() {
    print_info "Setting up database..."
    python migrate.py --action setup
    if [ $? -eq 0 ]; then
        print_status "Database setup completed"
    else
        print_error "Database setup failed"
        return 1
    fi
}

# Function to create directories
create_directories() {
    print_info "Creating necessary directories..."
    mkdir -p logs uploads/dev uploads/prod email_notifications tests
    print_status "Directories created"
}

# Function to run tests
run_tests() {
    print_info "Running tests..."
    pytest -v
    if [ $? -eq 0 ]; then
        print_status "All tests passed"
    else
        print_warning "Some tests failed"
    fi
}

# Function to start server
start_server() {
    print_info "Starting development server..."
    print_info "Server will be available at: http://localhost:8000"
    print_info "API documentation: http://localhost:8000/docs"
    print_info "Press Ctrl+C to stop the server"
    python main.py
}

# Main setup function
main() {
    echo -e "${BLUE}🚀 Service Marketplace API Setup${NC}"
    echo "=================================="
    
    # Check prerequisites
    print_info "Checking prerequisites..."
    check_python || exit 1
    check_postgresql || exit 1
    
    # Create virtual environment
    create_venv
    activate_venv
    
    # Install dependencies
    install_dependencies
    
    # Create directories
    create_directories
    
    # Setup environment
    setup_environment "$1"
    
    # Setup database
    setup_database
    
    # Run tests
    run_tests
    
    print_status "Setup completed successfully!"
    echo ""
    print_info "Next steps:"
    print_info "1. Update .env file with your configuration"
    print_info "2. Start the server: ./setup.sh start"
    print_info "3. Visit http://localhost:8000/docs for API documentation"
}

# Function to show help
show_help() {
    echo "Service Marketplace API Setup Script"
    echo ""
    echo "Usage: $0 [COMMAND] [ENVIRONMENT]"
    echo ""
    echo "Commands:"
    echo "  setup     - Complete setup (default)"
    echo "  start     - Start the development server"
    echo "  test      - Run tests"
    echo "  migrate   - Run database migrations"
    echo "  reset     - Reset database (⚠️ DESTROYS DATA)"
    echo "  help      - Show this help message"
    echo ""
    echo "Environments:"
    echo "  development - Development environment (default)"
    echo "  production  - Production environment"
    echo ""
    echo "Examples:"
    echo "  $0 setup development"
    echo "  $0 setup production"
    echo "  $0 start"
    echo "  $0 test"
}

# Handle commands
case "${1:-setup}" in
    "setup")
        main "${2:-development}"
        ;;
    "start")
        activate_venv
        start_server
        ;;
    "test")
        activate_venv
        run_tests
        ;;
    "migrate")
        activate_venv
        python migrate.py --action migrate
        ;;
    "reset")
        activate_venv
        print_warning "This will destroy all data in the database!"
        read -p "Are you sure? (yes/no): " confirm
        if [ "$confirm" = "yes" ]; then
            python migrate.py --action reset
        else
            print_info "Reset cancelled"
        fi
        ;;
    "help"|"-h"|"--help")
        show_help
        ;;
    *)
        print_error "Unknown command: $1"
        show_help
        exit 1
        ;;
esac
