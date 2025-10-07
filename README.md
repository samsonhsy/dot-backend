# dot-backend

Backend API for the dot project built with FastAPI and PostgreSQL (Supabase).

## Quick Setup

### 1. Clone and Setup

```bash
# Clone the repository
git clone https://github.com/samsonhsy/dot-backend.git
cd dot-backend

# Install dependencies using uv
uv sync
```

### 2. Configure Database

```bash
# Copy the environment template
cp .env.example .env

# Edit .env and add the database credentials
# Ask me for the DATABASE_URL
```

Your `.env` should look like:
```
DATABASE_URL=postgresql+asyncpg://postgres:[PASSWORD]@db.[PROJECT].supabase.co:6543/postgres

```

### 3. Run the Development Server

```bash
# Using uvicorn
uvicorn main:app --reload

# The API will be available at:
# http://localhost:8000
# SWAGGER UI will be available at:
# http://localhost:8000/docs

```

## Development Notes

- Use `uv sync` to install/update dependencies
- Use `uv add <package>` to add new packages
- Database is hosted on Supabase (PostgreSQL)
