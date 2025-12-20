# dot-backend

FastAPI backend for the dot project. The repository now includes a self-contained Docker Compose stack featuring:

- **PostgreSQL 15** for relational data
- **MinIO** for S3-compatible object storage (bucket: `dot-s3`)
- **Uvicorn** app container running this FastAPI service

Use the Render deployment at https://dot-backend-85b8.onrender.com for quick demos (uptime not guaranteed), or run the stack locally with Docker.

## Prerequisites

- Docker Engine ≥ 20.10 and the Docker Compose plugin
- `uv` (optional) if you plan to run the app outside Docker

## 1. Configure Environment Variables

```bash
cp .env.example .env
```

Update `.env` with your secrets. Important keys:

| Variable | Description |
| --- | --- |
| `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD` | Provisioned inside the PostgreSQL container |
| `DATABASE_URL` | Connection string consumed by FastAPI (defaults to the internal DB service) |
| `S3_ACCESS_KEY`, `S3_SECRET_KEY` | Root credentials for MinIO and also the keys the app uses |
| `FILE_STORAGE_URL` | Defaults to `http://minio:9000` so the backend can reach MinIO over the Compose network |
| `SECRET_KEY`, `ACCESS_TOKEN_EXPIRE_HOURS` | JWT settings |

> 💡 If you prefer Supabase and cloud S3, keep the Docker stack off and replace `DATABASE_URL`/`FILE_STORAGE_*` in `.env` with your hosted values.

## 2. Run Everything with Docker Compose

```bash
docker compose up -d --build
```

Prefer a single command that also validates your configuration? Run `./scripts/setup.sh` (after `chmod +x scripts/setup.sh`). It wraps the same Compose command, waits briefly, and prints the service URLs for convenience.

What happens:

1. PostgreSQL container seeds the `punkt_db` database and exposes port `5432`.
2. MinIO container exposes `9000` (API) and `9001` (console) so you can manage buckets via the UI.
3. The backend container boots Uvicorn on port `8000` once the images are built.

After the first start, create the `dot-s3` bucket (the service expects this name):

- **Option A:** open http://localhost:9001, sign in with the credentials from `.env`, and create the bucket manually.
- **Option B:** run `docker compose exec minio mc mb -p dot-s3` (the `mc` client is pre-installed in the MinIO image).

### Helpful commands

```bash
docker compose ps                    # Status
docker compose logs -f backend       # Follow backend logs
docker compose exec backend pytest   # Run backend tests inside the container
docker compose down                  # Stop containers but keep volumes
docker compose down -v               # Stop everything and delete volumes
```

### Access points

- API: http://localhost:8000
- API docs: http://localhost:8000/docs
- MinIO console: http://localhost:9001 (use credentials from `.env`)
- PostgreSQL: `localhost:5432` (user/password from `.env`)

## 3. Using the Setup Script

```bash
chmod +x scripts/setup.sh
./scripts/setup.sh
```

The script verifies Docker/Compose availability, ensures `.env` exists, builds images, starts services, and prints handy URLs.

## 4. Local Development without Docker

```bash
uv sync
uvicorn main:app --reload
```

Set `DATABASE_URL` and the storage variables in `.env` to point to your preferred infrastructure (local Postgres, Supabase, etc.).

## 5. Render Deployment

- Render service URL: https://dot-backend-85b8.onrender.com
- The Render instance also runs `uvicorn main:app`. Because uptime isn’t guaranteed, rely on the Docker Compose stack for reproducible testing and demos.

## Troubleshooting

| Symptom | Fix |
| --- | --- |
| Backend exits with `psycopg`/`asyncpg` errors | Double‑check `DATABASE_URL` and ensure the `db` service is healthy (`docker compose logs db`). |
| Upload endpoints return 500s | Ensure the `dot-s3` bucket exists (create it via the console or `docker compose exec minio mc mb -p dot-s3`) and verify `FILE_STORAGE_*` credentials. |
| MinIO console not loading | Port `9001` might already be used—stop the conflicting service or change the port mapping in `docker-compose.yml`. |

## Contributing

- Use `uv sync` before committing Python changes.
- Run `pytest` (locally or via `docker compose exec backend pytest`).
- Keep `.env` out of version control.
