#!/bin/bash

# PostgreSQL + pgvector Setup Script
# This script automates the database setup for Investment AI

set -e  # Exit on error

echo "🚀 Investment AI - PostgreSQL Setup"
echo "===================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if .env file exists
if [ ! -f .env ]; then
    echo -e "${RED}Error: .env file not found!${NC}"
    echo "Please create .env file with DATABASE_URL configuration"
    exit 1
fi

# Load environment variables
source .env

echo -e "${YELLOW}Step 1: Checking PostgreSQL...${NC}"
if command -v psql &> /dev/null; then
    echo -e "${GREEN}✓ PostgreSQL CLI found${NC}"
else
    echo -e "${RED}✗ PostgreSQL not found${NC}"
    echo ""
    echo "Install PostgreSQL:"
    echo "  macOS:  brew install postgresql@16"
    echo "  Ubuntu: sudo apt install postgresql"
    echo "  Docker: docker run -d --name investment-ai-postgres -e POSTGRES_USER=investment_user -e POSTGRES_PASSWORD=investment_pass -e POSTGRES_DB=investment_ai -p 5432:5432 postgres:16"
    exit 1
fi

echo ""
echo -e "${YELLOW}Step 2: Testing database connection...${NC}"
# Extract connection details from DATABASE_URL
# Format: postgresql+asyncpg://user:pass@host:port/dbname
DB_HOST=$(echo $DATABASE_URL | sed -n 's/.*@\(.*\):.*/\1/p')
DB_PORT=$(echo $DATABASE_URL | sed -n 's/.*:\([0-9]*\)\/.*/\1/p')
DB_NAME=$(echo $DATABASE_URL | sed -n 's/.*\/\(.*\)/\1/p')
DB_USER=$(echo $DATABASE_URL | sed -n 's/.*:\/\/\(.*\):.*/\1/p')

if psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -c "SELECT 1" &> /dev/null; then
    echo -e "${GREEN}✓ Database connection successful${NC}"
else
    echo -e "${RED}✗ Cannot connect to database${NC}"
    echo ""
    echo "Make sure:"
    echo "  1. PostgreSQL is running"
    echo "  2. Database '$DB_NAME' exists"
    echo "  3. User '$DB_USER' has access"
    echo ""
    echo "Create database:"
    echo "  psql postgres"
    echo "  CREATE USER $DB_USER WITH PASSWORD 'your_password';"
    echo "  CREATE DATABASE $DB_NAME OWNER $DB_USER;"
    exit 1
fi

echo ""
echo -e "${YELLOW}Step 3: Installing pgvector extension...${NC}"
psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -c "CREATE EXTENSION IF NOT EXISTS vector;" &> /dev/null
echo -e "${GREEN}✓ pgvector extension enabled${NC}"

echo ""
echo -e "${YELLOW}Step 4: Running database migrations...${NC}"
cd backend

# Check if alembic is installed
if ! command -v alembic &> /dev/null; then
    echo -e "${RED}✗ Alembic not found${NC}"
    echo "Installing dependencies..."
    source ../venv/bin/activate
    pip install -r ../requirements.txt
fi

# Check if migration files exist
if [ ! -d "alembic/versions" ] || [ -z "$(ls -A alembic/versions)" ]; then
    echo "Creating initial migration..."
    alembic revision --autogenerate -m "Initial schema with pgvector"
fi

# Run migrations
echo "Applying migrations..."
alembic upgrade head

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Migrations applied successfully${NC}"
else
    echo -e "${RED}✗ Migration failed${NC}"
    exit 1
fi

cd ..

echo ""
echo -e "${YELLOW}Step 5: Verifying database schema...${NC}"
TABLE_COUNT=$(psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';")
echo -e "${GREEN}✓ Found $TABLE_COUNT tables${NC}"

echo ""
echo -e "${YELLOW}Step 6: Creating vector search index...${NC}"
psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -c "
CREATE INDEX IF NOT EXISTS idx_document_embeddings_vector 
ON document_embeddings 
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);
" &> /dev/null
echo -e "${GREEN}✓ HNSW index created for fast vector search${NC}"

echo ""
echo "=========================================="
echo -e "${GREEN}✅ Database setup complete!${NC}"
echo "=========================================="
echo ""
echo "Next steps:"
echo "  1. Update file upload API to use database"
echo "  2. Update analysis API to save results"
echo "  3. Create search endpoints"
echo "  4. Test with sample documents"
echo ""
echo "Quick test:"
echo "  cd backend"
echo "  python -c 'import asyncio; from config.database import test_connection; asyncio.run(test_connection())'"
echo ""
echo "Documentation:"
echo "  - docs/DATABASE_SETUP.md"
echo "  - docs/DATABASE_MIGRATION_SUMMARY.md"
echo ""
