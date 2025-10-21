#!/bin/bash
set -e

echo "🚀 Starting Service Marketplace API Container"
echo "=============================================="

# Wait for database to be ready
echo "⏳ Waiting for database to be ready..."
until python -c "
import time
import sys
from database import engine
from sqlalchemy import text

max_retries = 30
retry_count = 0

while retry_count < max_retries:
    try:
        with engine.connect() as conn:
            conn.execute(text('SELECT 1'))
        print('✅ Database connection successful')
        break
    except Exception as e:
        retry_count += 1
        if retry_count >= max_retries:
            print(f'❌ Database connection failed after {max_retries} retries: {e}')
            sys.exit(1)
        print(f'⏳ Database not ready, retrying in 2 seconds... (attempt {retry_count}/{max_retries})')
        time.sleep(2)
"; do
    echo "Database connection failed, retrying..."
    sleep 2
done

# Run database migrations
echo "🔄 Running database migrations..."
python migrate.py --action migrate

# Run database seeding (if no data exists)
echo "🌱 Checking if database needs seeding..."
python migrate.py --action seed

# Start the FastAPI application
echo "🚀 Starting FastAPI application..."
exec uvicorn main:app --host 0.0.0.0 --port 8000
