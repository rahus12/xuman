# 🐳 Docker Setup for Service Marketplace API

This document provides comprehensive instructions for containerizing and running the Service Marketplace API using Docker.

## 📋 Prerequisites

- Docker (version 20.10+)
- Docker Compose (version 2.0+)
- Git

## 🚀 Quick Start

### Option 1: Using the Setup Script (Recommended)

```bash
# Make the script executable and run it
chmod +x docker-setup.sh
./docker-setup.sh setup
```

### Option 2: Manual Setup

```bash
# 1. Create environment file
cp env.docker.template .env

# 2. Create necessary directories
mkdir -p logs email_notifications ssl

# 3. Build and start services
docker-compose up --build -d

# 4. Wait for services to be ready
docker-compose exec postgres pg_isready -U postgres
curl -f http://localhost:8000/health

# 5. Run database migrations
docker-compose exec app python migrate.py
```

## 🏗️ Architecture

The Docker setup includes the following services:

| Service | Description | Port | Purpose |
|---------|-------------|------|---------|
| **app** | FastAPI Application | 8000 | Main API service |
| **postgres** | PostgreSQL Database | 5432 | Data persistence |
| **redis** | Redis Cache | 6379 | Caching and sessions |
| **nginx** | Reverse Proxy | 80/443 | Load balancing and SSL |

## 📁 File Structure

```
├── Dockerfile                 # Application container definition
├── docker-compose.yml         # Multi-container orchestration
├── .dockerignore             # Files to exclude from Docker context
├── nginx.conf                # Nginx reverse proxy configuration
├── init.sql                  # Database initialization script
├── env.docker.template       # Docker environment template
├── docker-setup.sh           # Setup automation script
└── DOCKER_README.md          # This documentation
```

## 🔧 Configuration

### Environment Variables

Copy `env.docker.template` to `.env` and customize:

```bash
# Database
POSTGRES_DB=marketplace
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres123

# JWT Security
JWT_SECRET_KEY=your-super-secret-jwt-key-change-in-production

# Application
DEBUG=false
LOG_LEVEL=INFO

# Payment
PAYMENT_FAILURE_RATE=0.1
```

### Docker Compose Services

#### Application Service
- **Image**: Built from local Dockerfile
- **Port**: 8000 (internal), mapped to 8000 (host)
- **Dependencies**: PostgreSQL, Redis
- **Volumes**: Logs, email notifications

#### Database Service
- **Image**: postgres:15-alpine
- **Port**: 5432
- **Volume**: Persistent data storage
- **Health Check**: PostgreSQL readiness

#### Redis Service
- **Image**: redis:7-alpine
- **Port**: 6379
- **Volume**: Persistent cache data
- **Health Check**: Redis ping

#### Nginx Service
- **Image**: nginx:alpine
- **Ports**: 80, 443
- **Configuration**: Reverse proxy with SSL support

## 🛠️ Management Commands

### Using the Setup Script

```bash
# Interactive menu
./docker-setup.sh

# Direct commands
./docker-setup.sh setup    # Full setup
./docker-setup.sh start     # Start services
./docker-setup.sh stop      # Stop services
./docker-setup.sh status    # Show status
./docker-setup.sh logs      # Show logs
./docker-setup.sh migrate   # Run migrations
./docker-setup.sh cleanup   # Clean everything
```

### Using Docker Compose Directly

```bash
# Start all services
docker-compose up -d

# Start specific service
docker-compose up -d app

# View logs
docker-compose logs -f app

# Execute commands in container
docker-compose exec app python migrate.py
docker-compose exec app bash

# Stop services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

## 🔍 Monitoring and Debugging

### Health Checks

```bash
# Application health
curl http://localhost:8000/health

# Database health
docker-compose exec postgres pg_isready -U postgres

# Redis health
docker-compose exec redis redis-cli ping
```

### Logs

```bash
# All services
docker-compose logs

# Specific service
docker-compose logs app
docker-compose logs postgres
docker-compose logs nginx

# Follow logs in real-time
docker-compose logs -f app
```

### Container Access

```bash
# Access application container
docker-compose exec app bash

# Access database
docker-compose exec postgres psql -U postgres -d marketplace

# Access Redis
docker-compose exec redis redis-cli
```

## 🚀 Production Deployment

### Security Considerations

1. **Change default passwords** in `.env`
2. **Use strong JWT secrets**
3. **Enable SSL/TLS** with proper certificates
4. **Configure firewall** rules
5. **Use secrets management** for sensitive data

### SSL/TLS Setup

1. Place SSL certificates in `ssl/` directory:
   ```bash
   ssl/
   ├── cert.pem
   └── key.pem
   ```

2. Uncomment HTTPS configuration in `nginx.conf`

3. Update environment variables:
   ```bash
   SSL_CERT_PATH=/etc/nginx/ssl/cert.pem
   SSL_KEY_PATH=/etc/nginx/ssl/key.pem
   ```

### Scaling

```bash
# Scale application instances
docker-compose up --scale app=3

# Use external database
# Update DATABASE_URL in .env to point to external PostgreSQL
```

## 🧹 Maintenance

### Backup Database

```bash
# Create backup
docker-compose exec postgres pg_dump -U postgres marketplace > backup.sql

# Restore backup
docker-compose exec -T postgres psql -U postgres marketplace < backup.sql
```

### Update Application

```bash
# Pull latest changes
git pull

# Rebuild and restart
docker-compose up --build -d

# Run migrations
docker-compose exec app python migrate.py
```

### Clean Up

```bash
# Remove containers and volumes
docker-compose down -v

# Remove images
docker-compose down --rmi all

# Clean up system
docker system prune -a
```

## 🐛 Troubleshooting

### Common Issues

1. **Port conflicts**: Change ports in `docker-compose.yml`
2. **Permission issues**: Check file permissions and ownership
3. **Database connection**: Verify DATABASE_URL and network connectivity
4. **Memory issues**: Increase Docker memory limits

### Debug Commands

```bash
# Check container status
docker-compose ps

# Check container logs
docker-compose logs app

# Check resource usage
docker stats

# Inspect container
docker-compose exec app env
```

## 📊 Performance Optimization

### Resource Limits

Add to `docker-compose.yml`:

```yaml
services:
  app:
    deploy:
      resources:
        limits:
          memory: 512M
          cpus: '0.5'
        reservations:
          memory: 256M
          cpus: '0.25'
```

### Caching

- Use Redis for session storage
- Enable Nginx caching
- Use CDN for static assets

## 🔗 URLs and Endpoints

Once running, access:

- **API**: http://localhost:8000
- **Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Database**: localhost:5432
- **Redis**: localhost:6379

## 📝 Notes

- All data is persisted in Docker volumes
- Logs are stored in `logs/` directory
- Email notifications are stored in `email_notifications/`
- Use `docker-compose down -v` to completely reset the environment
