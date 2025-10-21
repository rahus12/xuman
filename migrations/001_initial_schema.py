"""
Initial database schema migration
Creates all core tables for the service marketplace application
"""

from sqlalchemy import text
from database import engine

def up():
    """Apply migration - create initial schema"""
    with engine.connect() as conn:
        # Create users table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS users (
                id UUID PRIMARY KEY,
                email VARCHAR(255) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                role VARCHAR(20) NOT NULL CHECK (role IN ('customer', 'provider')),
                profile JSON NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            )
        """))
        
        # Create services table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS services (
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
            )
        """))

        # Create bookings table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS bookings (
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
            )
        """))

        # Create password reset tokens table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS password_reset_tokens (
                id UUID PRIMARY KEY,
                email VARCHAR(255) NOT NULL,
                token VARCHAR(255) UNIQUE NOT NULL,
                expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
                is_used BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            )
        """))

        # Create payments table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS payments (
                id UUID PRIMARY KEY,
                booking_id UUID NOT NULL,
                status VARCHAR(20) NOT NULL CHECK (status IN ('pending', 'completed', 'failed', 'refunded')),
                transaction_id VARCHAR(255) UNIQUE NOT NULL,
                amount DECIMAL(10,2) NOT NULL CHECK (amount > 0),
                currency VARCHAR(3) DEFAULT 'USD',
                payment_method JSON NOT NULL,
                failure_reason TEXT,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            )
        """))

        # Create refunds table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS refunds (
                id UUID PRIMARY KEY,
                payment_id UUID NOT NULL,
                status VARCHAR(20) NOT NULL CHECK (status IN ('pending', 'completed', 'failed')),
                amount DECIMAL(10,2) NOT NULL CHECK (amount > 0),
                reason TEXT,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            )
        """))

        # Create notifications table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS notifications (
                id UUID PRIMARY KEY,
                user_id VARCHAR(255) NOT NULL,
                type VARCHAR(50) NOT NULL,
                title VARCHAR(255) NOT NULL,
                message TEXT NOT NULL,
                data JSONB,
                is_read BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                read_at TIMESTAMP WITH TIME ZONE
            )
        """))

        # Create migration tracking table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS migrations (
                id SERIAL PRIMARY KEY,
                version VARCHAR(50) UNIQUE NOT NULL,
                applied_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            )
        """))

        conn.commit()
    print("✅ Migration 001_initial_schema applied successfully")

def down():
    """Rollback migration - drop all tables"""
    with engine.connect() as conn:
        # Drop tables in reverse order to handle foreign key constraints
        tables = [
            'notifications',
            'refunds', 
            'payments',
            'password_reset_tokens',
            'bookings',
            'services',
            'users',
            'migrations'
        ]
        
        for table in tables:
            conn.execute(text(f"DROP TABLE IF EXISTS {table} CASCADE"))
        
        conn.commit()
    print("✅ Migration 001_initial_schema rolled back successfully")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "down":
        down()
    else:
        up()
