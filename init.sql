-- Database initialization script for Docker
-- This script runs when the PostgreSQL container starts for the first time

-- Create database if it doesn't exist (PostgreSQL will create it automatically)
-- But we can set up initial configurations here

-- Create extensions if needed
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Set timezone
SET timezone = 'UTC';

-- Create any initial users or configurations
-- (The application will handle table creation through migrations)
