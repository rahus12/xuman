from database import engine
from sqlalchemy import text

def create_tables():
    """Create all database tables"""
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

        # Create indexes
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)
        """))
        
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_services_provider_id ON services(provider_id)
        """))
        
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_services_category ON services(category)
        """))
        
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_bookings_customer_id ON bookings(customer_id)
        """))
        
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_bookings_provider_id ON bookings(provider_id)
        """))
        
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_bookings_service_id ON bookings(service_id)
        """))

        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_password_reset_tokens_token ON password_reset_tokens(token)
        """))

        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_password_reset_tokens_email ON password_reset_tokens(email)
        """))

        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_password_reset_tokens_expires_at ON password_reset_tokens(expires_at)
        """))

        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_payments_booking_id ON payments(booking_id)
        """))

        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_payments_transaction_id ON payments(transaction_id)
        """))

        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_payments_status ON payments(status)
        """))

        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_refunds_payment_id ON refunds(payment_id)
        """))

        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_refunds_status ON refunds(status)
        """))

        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_notifications_user_id ON notifications(user_id)
        """))

        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_notifications_type ON notifications(type)
        """))

        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_notifications_created_at ON notifications(created_at)
        """))

        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_notifications_is_read ON notifications(is_read)
        """))

        conn.commit()
    print("Database tables created successfully!")

if __name__ == "__main__":
    create_tables()
