FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (e.g. libpq for psycopg2 if needing source build, but binary usually ok)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project
COPY . .

# Expose port
EXPOSE 8000

# Give execution permissions to start.sh
RUN chmod +x /app/start.sh

# Run command
CMD ["./start.sh"]
