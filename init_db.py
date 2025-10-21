"""
Database initialization script
Creates all necessary tables and initial data
"""

import os
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from database import engine

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_tables():
    """Create all database tables using raw SQL"""
    try:
        logger.info("Creating database tables...")
        
        with engine.connect() as conn:
            # Create ENUM types
            conn.execute(text("""
                DO $$ BEGIN
                    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'userrole') THEN
                        CREATE TYPE UserRole AS ENUM ('CUSTOMER', 'PROVIDER');
                    END IF;
                    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'servicestatus') THEN
                        CREATE TYPE ServiceStatus AS ENUM ('ACTIVE', 'INACTIVE', 'PENDING');
                    END IF;
                    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'bookingstatus') THEN
                        CREATE TYPE BookingStatus AS ENUM ('PENDING', 'CONFIRMED', 'CANCELLED', 'COMPLETED');
                    END IF;
                END $$;
            """))
            
            # Create users table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS users (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    email VARCHAR(255) UNIQUE NOT NULL,
                    password VARCHAR(255) NOT NULL,
                    role UserRole NOT NULL,
                    profile JSONB NOT NULL,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """))
            
            # Create services table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS services (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    provider_id UUID NOT NULL REFERENCES users(id),
                    name VARCHAR(255) NOT NULL,
                    description TEXT,
                    price NUMERIC(10, 2) NOT NULL,
                    duration_minutes INTEGER NOT NULL,
                    availability JSONB NOT NULL DEFAULT '{}',
                    status ServiceStatus DEFAULT 'PENDING',
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """))
            
            # Create bookings table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS bookings (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    customer_id UUID NOT NULL REFERENCES users(id),
                    service_id UUID NOT NULL REFERENCES services(id),
                    provider_id UUID NOT NULL REFERENCES users(id),
                    status BookingStatus DEFAULT 'PENDING',
                    scheduled_at TIMESTAMP WITH TIME ZONE NOT NULL,
                    duration_minutes INTEGER NOT NULL,
                    total_amount NUMERIC(10, 2) NOT NULL,
                    notes TEXT,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """))
            
            # Create payments table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS payments (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    booking_id UUID UNIQUE NOT NULL REFERENCES bookings(id),
                    amount NUMERIC(10, 2) NOT NULL,
                    currency VARCHAR(10) NOT NULL,
                    payment_method JSONB NOT NULL,
                    status VARCHAR(50) NOT NULL,
                    transaction_id VARCHAR(255) UNIQUE,
                    failure_reason TEXT,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """))
            
            # Create password_reset_tokens table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS password_reset_tokens (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    email VARCHAR(255) NOT NULL REFERENCES users(email),
                    token VARCHAR(255) UNIQUE NOT NULL,
                    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
                    is_used BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """))
            
            # Create notifications table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS notifications (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    user_id VARCHAR(255) NOT NULL,
                    type VARCHAR(50) NOT NULL,
                    title VARCHAR(255) NOT NULL,
                    message TEXT NOT NULL,
                    data JSONB,
                    is_read BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    read_at TIMESTAMP WITH TIME ZONE
                );
            """))
            
            # Create indexes
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_users_email ON users (email);"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_services_provider_id ON services (provider_id);"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_bookings_customer_id ON bookings (customer_id);"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_bookings_service_id ON bookings (service_id);"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_bookings_provider_id ON bookings (provider_id);"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_payments_booking_id ON payments (booking_id);"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_password_reset_tokens_email ON password_reset_tokens (email);"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_password_reset_tokens_token ON password_reset_tokens (token);"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_notifications_user_id ON notifications (user_id);"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_notifications_is_read ON notifications (is_read);"))
            
            conn.commit()
        
        logger.info("✅ Database tables created successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to create tables: {e}")
        return False

def drop_tables():
    """Drop all database tables"""
    try:
        logger.info("Dropping database tables...")
        
        with engine.connect() as conn:
            # Drop all tables
            conn.execute(text("DROP SCHEMA public CASCADE"))
            conn.execute(text("CREATE SCHEMA public"))
            conn.commit()
        
        logger.info("✅ Database tables dropped successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to drop tables: {e}")
        return False

def reset_database():
    """Reset database (drop and recreate all tables)"""
    try:
        logger.info("Resetting database...")
        
        # Drop all tables
        if not drop_tables():
            return False
            
        # Create all tables
        if not create_tables():
            return False
            
        logger.info("✅ Database reset completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to reset database: {e}")
        return False

def seed_initial_data():
    """Seed database with initial data"""
    try:
        logger.info("Seeding initial data...")
        
        # Create a session
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        try:
            # Add any initial data here if needed
            # For now, we'll just create the tables
            logger.info("✅ Initial data seeded successfully")
            return True
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"❌ Failed to seed initial data: {e}")
        return False

if __name__ == "__main__":
    """Run database initialization"""
    import sys
    
    if len(sys.argv) > 1:
        action = sys.argv[1]
        
        if action == "create":
            success = create_tables()
        elif action == "drop":
            success = drop_tables()
        elif action == "reset":
            success = reset_database()
        elif action == "seed":
            success = seed_initial_data()
        else:
            logger.error("Invalid action. Use: create, drop, reset, or seed")
            success = False
    else:
        # Default: create tables
        success = create_tables()
    
    sys.exit(0 if success else 1)