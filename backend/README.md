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
* `POST /ngos`: Create a new NGO.
* `GET /ngos/discover`: List discoverable NGOs (public and verified).
* `GET /ngos/slug/{slug}`: Get NGO by slug.
* `PUT /ngos/{ngo_id}`: Update NGO.
* `POST /ngos/{ngo_id}/verify`: Submit an NGO for verification.
* `POST /auth/login`: Authenticate with an email and password to receive an access token and refresh token.
* `POST /auth/refresh`: Submit a valid refresh token in the body `{"refresh_token": "..."}` to receive a new pair of access and refresh tokens.
* `POST /auth/google`: Login or register a user via Google Sign-In. Accepts `{"id_token": "..."}` where `id_token` is the Google identity token from the client.
* `GET /auth/me`: A protected endpoint that returns the currently authenticated user's details. Requires a valid access token in the `Authorization` header (`Bearer <token>`).

### Google Sign-In Support

Google Sign-In allows users to authenticate using their Google accounts. The flow works as follows:
1. The client (e.g. Flutter app) authenticates the user with Google and receives a Google `id_token`.
2. The client sends a `POST` request to `/auth/google` with a JSON payload: `{"id_token": "..."}`.
3. The backend uses Google's public keys to verify the token server-side.
4. If valid, the backend extracts the user's `email`, `sub` (Google's unique user ID), and `name`.
5. The backend looks up the user by email. If the user does not exist, a new user is created.
6. The user is linked to the Google provider in the `auth_providers` table.
7. The backend returns its own JWT access and refresh tokens.

#### Required Environment Variable
For Google Sign-In verification to work securely in production, ensure that the `.env` file specifies the client ID assigned by Google:

```dotenv
GOOGLE_CLIENT_ID="your-google-client-id.apps.googleusercontent.com"
```

### Security Note
For the MVP, a stateless refresh token strategy is implemented. It relies on the JWT secret and expiration time.

### Running Tests

To run the authentication tests, execute:
```bash
pytest app/tests/test_auth.py
```
This requires `pytest` and `httpx` to be installed (included in `requirements.txt`).
