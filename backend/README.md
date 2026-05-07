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

## Authentication

The backend uses JWT (JSON Web Tokens) for authentication.

### Endpoints
* `POST /auth/register`: Register a new user with an email, password, and optional full name.
* `POST /auth/login`: Authenticate with an email and password to receive an access token and refresh token.
* `POST /auth/refresh`: Submit a valid refresh token in the body `{"refresh_token": "..."}` to receive a new pair of access and refresh tokens.
* `GET /auth/me`: A protected endpoint that returns the currently authenticated user's details. Requires a valid access token in the `Authorization` header (`Bearer <token>`).

### Security Note
For the MVP, a stateless refresh token strategy is implemented. It relies on the JWT secret and expiration time.

### Running Tests

To run the authentication tests, execute:
```bash
pytest app/tests/test_auth.py
```
This requires `pytest` and `httpx` to be installed (included in `requirements.txt`).
