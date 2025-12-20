#!/bin/bash
# setup.sh

set -euo pipefail

echo "Punkt Backend Docker Setup Script"

# Check if Docker is installed
if ! [ -x "$(command -v docker)" ]; then
  echo "Error: Docker is not installed." >&2
  exit 1
fi

# Check if Docker Compose is available
if ! [ -x "$(command -v docker compose)" ]; then
  echo "Error: Docker Compose is not installed." >&2
  exit 1
fi

# Create .env file from example if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file from example template..."
    cp .env.example .env
    echo "Please edit .env file to set your configuration values before proceeding."
    exit 1
fi

echo "Validating docker-compose.yml..."
docker compose config >/dev/null

echo "Starting Punkt backend services..."
docker compose up -d --build

echo "Waiting for services to be ready..."
sleep 10

# Check if services are running
echo "Checking service status..."
docker compose ps

echo "Punkt backend is now running!"
echo "API:              http://localhost:8000"
echo "API Docs:         http://localhost:8000/docs"
echo "MinIO Console:    http://localhost:9001 (use credentials from .env)"
echo "PostgreSQL:       localhost:5432 (${POSTGRES_DB:-punkt_db})"