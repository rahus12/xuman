# Database Documentation

## Overview
The Service Marketplace API uses PostgreSQL as the primary database with SQLAlchemy as the ORM. The database is designed to support a service marketplace platform with users, services, bookings, and password reset functionality.

## Database Schema

### Users Table
Stores user account information including authentication and profile data.

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('customer', 'provider')),
    profile JSON NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

**Columns:**
- `id`: Primary key (UUID)
- `email`: Unique email address (VARCHAR)
- `password`: Hashed password using bcrypt (VARCHAR)
- `role`: User role - either 'customer' or 'provider' (VARCHAR)
- `profile`: JSON object containing user profile information (JSON)
- `created_at`: Timestamp when user was created (TIMESTAMP WITH TIME ZONE)
- `updated_at`: Timestamp when user was last updated (TIMESTAMP WITH TIME ZONE)

**Profile JSON Structure:**
```json
{
  "firstName": "string",
  "lastName": "string", 
  "phone": "string",
  "address": "string"
}
```

### Services Table
Stores service offerings from providers.

```sql
CREATE TABLE services (
    id UUID PRIMARY KEY,
    provider_id UUID NOT NULL,
    title VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    category VARCHAR(50) NOT NULL,
    price DECIMAL(10,2) NOT NULL CHECK (price > 0),
    currency VARCHAR(3) DEFAULT 'USD',
    duration INTEGER NOT NULL CHECK (duration > 0),
    availability JSON NOT NULL,
    images JSON DEFAULT '[]',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

**Columns:**
- `id`: Primary key (UUID)
- `provider_id`: Foreign key to users table (UUID)
- `title`: Service title (VARCHAR)
- `description`: Detailed service description (TEXT)
- `category`: Service category (VARCHAR)
- `price`: Service price (DECIMAL)
- `currency`: Currency code (VARCHAR)
- `duration`: Service duration in minutes (INTEGER)
- `availability`: JSON object with weekly availability schedule (JSON)
- `images`: Array of image URLs (JSON)
- `is_active`: Whether service is currently available (BOOLEAN)
- `created_at`: Timestamp when service was created (TIMESTAMP WITH TIME ZONE)

**Availability JSON Structure:**
```json
{
  "monday": [{"start": "09:00", "end": "17:00"}],
  "tuesday": [{"start": "09:00", "end": "17:00"}],
  "wednesday": [{"start": "09:00", "end": "17:00"}],
  "thursday": [{"start": "09:00", "end": "17:00"}],
  "friday": [{"start": "09:00", "end": "17:00"}],
  "saturday": [],
  "sunday": []
}
```

### Bookings Table
Stores booking information between customers and providers.

```sql
CREATE TABLE bookings (
    id UUID PRIMARY KEY,
    customer_id UUID NOT NULL,
    service_id UUID NOT NULL,
    provider_id UUID NOT NULL,
    status VARCHAR(20) NOT NULL CHECK (status IN ('pending', 'confirmed', 'completed', 'cancelled')),
    scheduled_at TIMESTAMP WITH TIME ZONE NOT NULL,
    duration INTEGER NOT NULL CHECK (duration > 0),
    total_amount DECIMAL(10,2) NOT NULL CHECK (total_amount > 0),
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

**Columns:**
- `id`: Primary key (UUID)
- `customer_id`: Foreign key to users table (UUID)
- `service_id`: Foreign key to services table (UUID)
- `provider_id`: Foreign key to users table (UUID)
- `status`: Booking status (VARCHAR)
- `scheduled_at`: When the service is scheduled (TIMESTAMP WITH TIME ZONE)
- `duration`: Booking duration in minutes (INTEGER)
- `total_amount`: Total cost of the booking (DECIMAL)
- `notes`: Additional notes for the booking (TEXT)
- `created_at`: Timestamp when booking was created (TIMESTAMP WITH TIME ZONE)

### Password Reset Tokens Table
Stores password reset tokens for secure password recovery.

```sql
CREATE TABLE password_reset_tokens (
    id UUID PRIMARY KEY,
    email VARCHAR(255) NOT NULL,
    token VARCHAR(255) UNIQUE NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    is_used BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

**Columns:**
- `id`: Primary key (UUID)
- `email`: Email address requesting password reset (VARCHAR)
- `token`: Unique reset token (VARCHAR)
- `expires_at`: When the token expires (TIMESTAMP WITH TIME ZONE)
- `is_used`: Whether the token has been used (BOOLEAN)
- `created_at`: Timestamp when token was created (TIMESTAMP WITH TIME ZONE)

## Indexes

### Performance Indexes
```sql
-- Users table indexes
CREATE INDEX idx_users_email ON users(email);

-- Services table indexes
CREATE INDEX idx_services_provider_id ON services(provider_id);
CREATE INDEX idx_services_category ON services(category);

-- Bookings table indexes
CREATE INDEX idx_bookings_customer_id ON bookings(customer_id);
CREATE INDEX idx_bookings_provider_id ON bookings(provider_id);
CREATE INDEX idx_bookings_service_id ON bookings(service_id);

-- Password reset tokens indexes
CREATE INDEX idx_password_reset_tokens_token ON password_reset_tokens(token);
CREATE INDEX idx_password_reset_tokens_email ON password_reset_tokens(email);
CREATE INDEX idx_password_reset_tokens_expires_at ON password_reset_tokens(expires_at);
```

## Relationships

### Foreign Key Relationships
- `services.provider_id` → `users.id` (Many-to-One)
- `bookings.customer_id` → `users.id` (Many-to-One)
- `bookings.service_id` → `services.id` (Many-to-One)
- `bookings.provider_id` → `users.id` (Many-to-One)

### Relationship Cardinality
- **Users to Services**: One-to-Many (One provider can have many services)
- **Users to Bookings (as Customer)**: One-to-Many (One customer can have many bookings)
- **Users to Bookings (as Provider)**: One-to-Many (One provider can have many bookings)
- **Services to Bookings**: One-to-Many (One service can have many bookings)

## Data Types

### UUID
- Used for all primary keys and foreign keys
- Generated using Python's `uuid.uuid4()`
- Provides globally unique identifiers

### JSON
- Used for flexible data structures (profile, availability, images)
- Allows schema evolution without table changes
- Validated at application level using Pydantic models

### Timestamps
- All timestamps use `TIMESTAMP WITH TIME ZONE`
- Stored in UTC timezone
- Converted to local timezone in API responses

### Decimal
- Used for monetary values (price, total_amount)
- Precision: 10 digits total, 2 decimal places
- Ensures accurate financial calculations

## Constraints

### Check Constraints
- `users.role`: Must be 'customer' or 'provider'
- `services.price`: Must be greater than 0
- `services.duration`: Must be greater than 0
- `bookings.status`: Must be 'pending', 'confirmed', 'completed', or 'cancelled'
- `bookings.duration`: Must be greater than 0
- `bookings.total_amount`: Must be greater than 0

### Unique Constraints
- `users.email`: Email addresses must be unique
- `password_reset_tokens.token`: Reset tokens must be unique

### Not Null Constraints
- All primary keys and foreign keys are NOT NULL
- Critical business fields (email, password, title, etc.) are NOT NULL

## Security Features

### Password Security
- Passwords are hashed using bcrypt with salt
- No plain text passwords are stored
- Password verification uses constant-time comparison

### SQL Injection Prevention
- All queries use parameterized statements
- No string concatenation in SQL queries
- Input validation at application level

### Token Security
- Password reset tokens are cryptographically secure
- Tokens expire after 24 hours
- Tokens are single-use (marked as used after consumption)
- Tokens are unique and unpredictable

## Database Operations

### Connection Management
- Uses SQLAlchemy connection pooling
- Automatic connection cleanup
- Transaction management with rollback on errors

### Query Optimization
- Indexes on frequently queried columns
- Efficient JOIN operations for related data
- Pagination support for large result sets

### Data Integrity
- Foreign key constraints ensure referential integrity
- Check constraints validate data at database level
- Transaction isolation prevents data corruption

## Migration Strategy

### Schema Changes
- Use Alembic for database migrations
- Version-controlled schema changes
- Rollback capability for failed migrations

### Data Migration
- Backup before major schema changes
- Gradual data migration for large datasets
- Validation after migration completion

## Backup and Recovery

### Backup Strategy
- Regular automated backups
- Point-in-time recovery capability
- Cross-region backup replication

### Recovery Procedures
- Documented recovery procedures
- Regular recovery testing
- Minimal downtime recovery options

## Monitoring and Maintenance

### Performance Monitoring
- Query performance tracking
- Index usage analysis
- Connection pool monitoring

### Maintenance Tasks
- Regular VACUUM operations
- Index rebuilding when necessary
- Statistics updates for query planner

## Environment Configuration

### Development
- Local PostgreSQL instance
- In-memory SQLite for testing
- Sample data for development

### Production
- Managed PostgreSQL service
- Read replicas for scaling
- Automated backups and monitoring

## Connection String Format
```
postgresql+psycopg://username:password@host:port/database_name
```

## Database URL Environment Variable
```bash
DATABASE_URL=postgresql+psycopg://vishalchamaria@localhost:5432/service_marketplace
```
