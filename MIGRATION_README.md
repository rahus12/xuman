# Database Migration and Environment Setup

This document explains how to set up the Service Marketplace API database and environment configuration.

## Quick Start

### 1. Automatic Setup
```bash
# Run the setup script (recommended for first-time setup)
./setup.sh setup development

# Or for production environment
./setup.sh setup production
```

### 2. Manual Setup
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Create environment file
# Create .env file with your configuration
# See Environment Variables section below for required settings

# 3. Setup database
python migrate.py --action setup
```

## Migration Script Usage

The `migrate.py` script provides various database operations:

### Available Actions

```bash
# Complete setup (create DB, run migrations, seed data)
python migrate.py --action setup

# Run migrations only
python migrate.py --action migrate

# Seed database with sample data
python migrate.py --action seed

# Reset database (⚠️ DESTROYS ALL DATA)
python migrate.py --action reset

# Check environment configuration
python migrate.py --action check

# Install dependencies
python migrate.py --action install
```

### Environment Configuration

The application uses a single `.env` file for configuration. Create this file with your settings:

### Environment Variables

#### Required Variables
```bash
DATABASE_URL=postgresql+psycopg://user:pass@host:port/dbname
JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
```

#### Optional Variables
```bash
# Application
DEBUG=true
HOST=0.0.0.0
PORT=8000

# Email (for notifications)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# File Upload
UPLOAD_DIR=uploads
MAX_FILE_SIZE=10485760

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60

# Redis (for caching)
REDIS_URL=redis://localhost:6379/0

# Payment Gateway (Mock)
PAYMENT_GATEWAY_URL=https://api.payment-gateway.com
PAYMENT_FAILURE_RATE=0.1
```

## Database Schema

The migration script creates the following tables:

### Core Tables
- **users** - User accounts and profiles
- **services** - Service listings
- **bookings** - Service bookings
- **payments** - Payment transactions
- **refunds** - Refund records
- **notifications** - Real-time notifications
- **password_reset_tokens** - Password reset functionality

### Indexes
The script also creates optimized indexes for:
- User email lookups
- Service provider and category searches
- Booking queries by customer/provider
- Payment and refund tracking
- Notification delivery

## Development Workflow

### First Time Setup
```bash
# 1. Clone repository
git clone <repository-url>
cd service-marketplace-api

# 2. Make setup script executable
chmod +x setup.sh

# 3. Run complete setup
./setup.sh setup development

# 4. Start development server
./setup.sh start
```

### Daily Development
```bash
# Start development server
./setup.sh start

# Run tests
./setup.sh test

# Check database status
python migrate.py --action check
```

### Database Changes
```bash
# After modifying database schema, update init_db.py
# Then run migrations
./setup.sh migrate

# Or reset and recreate (⚠️ DESTROYS DATA)
./setup.sh reset
```

## Production Deployment

### Environment Setup
```bash
# 1. Create .env file with production values
# - Set DATABASE_URL to production database
# - Set secure JWT_SECRET_KEY
# - Configure SMTP settings
# - Set DEBUG=false

# 2. Run production setup
./setup.sh setup production
```

### Security Checklist
- [ ] Change JWT_SECRET_KEY to a secure random string
- [ ] Set DEBUG=false
- [ ] Use production database credentials
- [ ] Configure proper CORS origins
- [ ] Set up SSL/TLS certificates
- [ ] Configure firewall rules
- [ ] Set up monitoring and logging

## Troubleshooting

### Common Issues

#### Database Connection Failed
```bash
# Check if PostgreSQL is running
pg_ctl status

# Check connection string
python migrate.py --action check

# Test connection manually
psql "postgresql://user:pass@host:port/dbname"
```

#### Migration Errors
```bash
# Check database permissions
# Ensure user has CREATE, DROP, and ALTER privileges

# Reset database if needed
python migrate.py --action reset
```

#### Environment Issues
```bash
# Check environment file
python migrate.py --action check

# Verify .env file exists and is readable
ls -la .env
cat .env
```

### Logs and Debugging

```bash
# Check application logs
tail -f logs/app.log

# Check database logs
tail -f /var/log/postgresql/postgresql.log

# Enable debug logging
export LOG_LEVEL=DEBUG
python main.py
```

## File Structure

```
service-marketplace-api/
├── migrate.py              # Migration script
├── setup.py               # Setup script
├── requirements.txt       # Python dependencies
├── env.example           # Environment template
├── env.development       # Development config
├── env.production        # Production config
├── init_db.py           # Database schema
├── database.py          # Database connection
├── main.py              # Application entry point
├── logs/                # Log files
├── uploads/             # File uploads
└── email_notifications/ # Email mock files
```

## Support

For issues with migration or setup:

1. Check the logs in `logs/` directory
2. Verify environment variables with `python migrate.py --action check`
3. Test database connection manually
4. Review the troubleshooting section above

## Next Steps

After successful setup:

1. **Start the server**: `python main.py`
2. **Visit API docs**: http://localhost:8000/docs
3. **Test endpoints**: Use the interactive Swagger UI
4. **Run tests**: `pytest`
5. **Deploy**: Follow production deployment guide
