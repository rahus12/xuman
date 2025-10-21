#!/usr/bin/env python3
"""
Database Migration Script for Service Marketplace API
This script handles database setup, migrations, and environment configuration.
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path
from dotenv import load_dotenv
from database import engine
from sqlalchemy import text
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_environment(env_file=".env"):
    """Load environment variables from file"""
    if os.path.exists(env_file):
        load_dotenv(env_file)
        logger.info(f"Loaded environment from {env_file}")
    else:
        logger.warning(f"Environment file {env_file} not found, using system environment variables")

def check_database_connection():
    """Check if database connection is working"""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("✅ Database connection successful")
        return True
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return False

def create_database():
    """Create database if it doesn't exist"""
    try:
        # Extract database name from DATABASE_URL
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            logger.error("DATABASE_URL not found in environment variables")
            return False
        
        # Parse database name from URL
        if "postgresql" in database_url:
            # Extract database name from postgresql://user:pass@host:port/dbname
            db_name = database_url.split("/")[-1]
            # Create connection to postgres database to create our database
            base_url = "/".join(database_url.split("/")[:-1])
            postgres_url = f"{base_url}/postgres"
            
            from sqlalchemy import create_engine
            postgres_engine = create_engine(postgres_url)
            
            with postgres_engine.connect() as conn:
                # Check if database exists
                result = conn.execute(text(f"SELECT 1 FROM pg_database WHERE datname = '{db_name}'"))
                if not result.fetchone():
                    conn.execute(text(f"CREATE DATABASE {db_name}"))
                    logger.info(f"✅ Database '{db_name}' created successfully")
                else:
                    logger.info(f"✅ Database '{db_name}' already exists")
            
            postgres_engine.dispose()
            return True
        else:
            logger.warning("Database creation only supported for PostgreSQL")
            return True
            
    except Exception as e:
        logger.error(f"❌ Failed to create database: {e}")
        return False

def run_migrations():
    """Run database migrations"""
    try:
        from init_db import create_tables
        create_tables()
        logger.info("✅ Database migrations completed successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        return False

def seed_database():
    """Seed database with initial data"""
    try:
        with engine.connect() as conn:
            # Check if we already have data
            result = conn.execute(text("SELECT COUNT(*) FROM users"))
            user_count = result.scalar()
            
            if user_count > 0:
                logger.info("Database already has data, skipping seed")
                return True
            
            # Insert sample data
            logger.info("Seeding database with sample data...")
            
            # Sample users
            conn.execute(text("""
                INSERT INTO users (id, email, password, role, profile, created_at, updated_at)
                VALUES 
                ('550e8400-e29b-41d4-a716-446655440001', 'admin@marketplace.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/9.8.8.8', 'PROVIDER', 
                 '{"firstName": "Admin", "lastName": "User", "phone": "+1234567890", "address": "123 Admin St"}', NOW(), NOW()),
                ('550e8400-e29b-41d4-a716-446655440002', 'provider@marketplace.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/9.8.8.8', 'PROVIDER',
                 '{"firstName": "Service", "lastName": "Provider", "phone": "+1234567891", "address": "456 Provider Ave"}', NOW(), NOW()),
                ('550e8400-e29b-41d4-a716-446655440003', 'customer@marketplace.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/9.8.8.8', 'CUSTOMER',
                 '{"firstName": "Test", "lastName": "Customer", "phone": "+1234567892", "address": "789 Customer Blvd"}', NOW(), NOW())
            """))
            
            # Sample services
            conn.execute(text("""
                INSERT INTO services (id, provider_id, name, description, price, duration_minutes, availability, status, created_at, updated_at)
                VALUES 
                ('660e8400-e29b-41d4-a716-446655440001', '550e8400-e29b-41d4-a716-446655440002', 'Web Development', 'Professional web development services', 100.00, 120, '{"monday": ["09:00", "17:00"], "tuesday": ["09:00", "17:00"], "wednesday": ["09:00", "17:00"], "thursday": ["09:00", "17:00"], "friday": ["09:00", "17:00"]}', 'ACTIVE', NOW(), NOW()),
                ('660e8400-e29b-41d4-a716-446655440002', '550e8400-e29b-41d4-a716-446655440002', 'Mobile App Development', 'iOS and Android app development', 150.00, 180, '{"monday": ["10:00", "18:00"], "tuesday": ["10:00", "18:00"], "wednesday": ["10:00", "18:00"], "thursday": ["10:00", "18:00"], "friday": ["10:00", "18:00"]}', 'ACTIVE', NOW(), NOW()),
                ('660e8400-e29b-41d4-a716-446655440003', '550e8400-e29b-41d4-a716-446655440001', 'Consulting', 'Business consulting services', 200.00, 60, '{"monday": ["08:00", "16:00"], "tuesday": ["08:00", "16:00"], "wednesday": ["08:00", "16:00"], "thursday": ["08:00", "16:00"], "friday": ["08:00", "16:00"]}', 'ACTIVE', NOW(), NOW())
            """))
            
            conn.commit()
            logger.info("✅ Database seeded successfully")
            return True
            
    except Exception as e:
        logger.error(f"❌ Database seeding failed: {e}")
        return False

def reset_database():
    """Reset database (drop and recreate all tables)"""
    try:
        logger.warning("⚠️  This will delete all data in the database!")
        confirm = input("Are you sure you want to reset the database? (yes/no): ")
        if confirm.lower() != 'yes':
            logger.info("Database reset cancelled")
            return False
        
        with engine.connect() as conn:
            # Drop all tables
            conn.execute(text("DROP SCHEMA public CASCADE"))
            conn.execute(text("CREATE SCHEMA public"))
            conn.commit()
            logger.info("✅ Database reset completed")
            
            # Recreate tables
            return run_migrations()
            
    except Exception as e:
        logger.error(f"❌ Database reset failed: {e}")
        return False

def check_environment():
    """Check if all required environment variables are set"""
    required_vars = [
        'DATABASE_URL',
        'JWT_SECRET_KEY',
        'JWT_ALGORITHM',
        'JWT_ACCESS_TOKEN_EXPIRE_MINUTES'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        logger.error(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        logger.info("Please check your .env file or set these variables")
        return False
    
    logger.info("✅ All required environment variables are set")
    return True

def install_dependencies():
    """Install Python dependencies"""
    try:
        logger.info("Installing Python dependencies...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        logger.info("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Failed to install dependencies: {e}")
        return False
    except FileNotFoundError:
        logger.error("❌ requirements.txt not found")
        return False

def main():
    """Main migration function"""
    parser = argparse.ArgumentParser(description="Service Marketplace API Migration Script")
    parser.add_argument("--env", default=".env", help="Environment file to load")
    parser.add_argument("--action", choices=["setup", "migrate", "seed", "reset", "check", "install"], 
                       default="setup", help="Action to perform")
    parser.add_argument("--force", action="store_true", help="Force operation without confirmation")
    
    args = parser.parse_args()
    
    logger.info("🚀 Service Marketplace API Migration Script")
    logger.info("=" * 50)
    
    # Load environment
    load_environment(args.env)
    
    if args.action == "install":
        return install_dependencies()
    
    if args.action == "check":
        return check_environment()
    
    if args.action == "setup":
        logger.info("Setting up database...")
        if not check_environment():
            return False
        
        if not create_database():
            return False
        
        if not check_database_connection():
            return False
        
        if not run_migrations():
            return False
        
        if not seed_database():
            return False
        
        logger.info("✅ Database setup completed successfully!")
        return True
    
    elif args.action == "migrate":
        logger.info("Running migrations...")
        if not check_database_connection():
            return False
        return run_migrations()
    
    elif args.action == "seed":
        logger.info("Seeding database...")
        if not check_database_connection():
            return False
        return seed_database()
    
    elif args.action == "reset":
        logger.info("Resetting database...")
        if not check_database_connection():
            return False
        return reset_database()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
