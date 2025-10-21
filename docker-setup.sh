#!/bin/bash

# Simple Docker Setup Script for Service Marketplace API
# This script sets up only the essential services: FastAPI app + PostgreSQL

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is installed
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    print_success "Docker and Docker Compose are installed"
}

# Create necessary directories
create_directories() {
    print_status "Creating necessary directories..."
    mkdir -p logs
    mkdir -p email_notifications
    print_success "Directories created"
}

# Setup environment file
setup_env() {
    if [ ! -f .env ]; then
        print_status "Creating .env file from template..."
        cp env.docker.template .env
        print_success ".env file created from template"
        print_warning "Please review and update the .env file with your configuration"
    else
        print_status ".env file already exists"
    fi
}

# Build and start services
start_services() {
    print_status "Building and starting Docker services (FastAPI + PostgreSQL only)..."
    docker-compose up --build -d
    print_success "Services started"
}

# Wait for services to be ready
wait_for_services() {
    print_status "Waiting for services to be ready..."
    
    # Wait for database
    print_status "Waiting for database..."
    timeout 60 bash -c 'until docker-compose exec postgres pg_isready -U postgres; do sleep 2; done'
    print_success "Database is ready"
    
    # Wait for application
    print_status "Waiting for application..."
    timeout 60 bash -c 'until curl -f http://localhost:8000/health > /dev/null 2>&1; do sleep 2; done'
    print_success "Application is ready"
}

# Run database migrations
run_migrations() {
    print_status "Running database migrations..."
    docker-compose exec app python migrate.py
    print_success "Database migrations completed"
}

# Show service status
show_status() {
    print_status "Service status:"
    docker-compose ps
    
    echo ""
    print_status "Application URLs:"
    echo "  - API: http://localhost:8000"
    echo "  - Docs: http://localhost:8000/docs"
    echo "  - Health: http://localhost:8000/health"
    echo "  - Database: localhost:5432"
}

# Show logs
show_logs() {
    print_status "Showing application logs (Ctrl+C to exit):"
    docker-compose logs -f app
}

# Stop services
stop_services() {
    print_status "Stopping services..."
    docker-compose down
    print_success "Services stopped"
}

# Clean up
cleanup() {
    print_status "Cleaning up Docker resources..."
    docker-compose down -v --remove-orphans
    docker system prune -f
    print_success "Cleanup completed"
}

# Main menu
show_menu() {
    echo ""
    echo "🐳 Simple Docker Setup for Service Marketplace API"
    echo "=================================================="
    echo "1. Setup and start services (FastAPI + PostgreSQL)"
    echo "2. Start services only"
    echo "3. Stop services"
    echo "4. Show service status"
    echo "5. Show application logs"
    echo "6. Run database migrations"
    echo "7. Clean up everything"
    echo "8. Exit"
    echo ""
}

# Main function
main() {
    case "${1:-menu}" in
        "setup")
            check_docker
            create_directories
            setup_env
            start_services
            wait_for_services
            run_migrations
            show_status
            ;;
        "start")
            start_services
            wait_for_services
            show_status
            ;;
        "stop")
            stop_services
            ;;
        "status")
            show_status
            ;;
        "logs")
            show_logs
            ;;
        "migrate")
            run_migrations
            ;;
        "cleanup")
            cleanup
            ;;
        "menu"|*)
            show_menu
            read -p "Choose an option (1-8): " choice
            case $choice in
                1) main setup ;;
                2) main start ;;
                3) main stop ;;
                4) main status ;;
                5) main logs ;;
                6) main migrate ;;
                7) main cleanup ;;
                8) exit 0 ;;
                *) print_error "Invalid option"; main ;;
            esac
            ;;
    esac
}

# Run main function with all arguments
main "$@"
