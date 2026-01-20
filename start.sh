#!/bin/bash

# Wait for database to be ready (optional but recommended)
# For now, we trust the DB is up since we have depends_on in docker-compose

# Run migrations
echo "Running database migrations..."
alembic upgrade head

# Start the application
echo "Starting application..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
