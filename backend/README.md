# NgoConnect Backend

This is the backend service for NgoConnect, built with FastAPI and PostgreSQL.

## Project Structure
- `app/main.py`: Entry point for the FastAPI application.
- `app/api/`: API routers and endpoints.
- `app/core/`: Application configuration and core settings.
- `app/db/`: Database connection and session setup.
- `app/models/`: SQLAlchemy declarative models.
- `app/repositories/`: Data access logic (CRUD).
- `app/schemas/`: Pydantic models for validation.
- `app/services/`: Business logic.
- `app/tests/`: Pytest test suite.

## Running the Application

Ensure you have Docker and Docker Compose installed.

To start the backend and the PostgreSQL database:
```bash
docker compose up -d
```

The API will be available at `http://localhost:8000`.

To view the Swagger API documentation, visit `http://localhost:8000/docs`.

### Database Migrations

Alembic is used for database migrations.

To create a new migration:
```bash
alembic revision --autogenerate -m "Migration description"
```

To run all pending migrations:
```bash
alembic upgrade head
```

### Check Health Status
```bash
curl http://localhost:8000/health
```
