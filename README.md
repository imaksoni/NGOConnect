# NgoConnect

Welcome to the NgoConnect project! This repository uses a monorepo structure containing both the mobile application and the backend service.

## Observability & Analytics

### Logging Approach
NgoConnect uses structured JSON logging in the backend (`app/core/logger.py`) and standard Dart developer logging on the frontend (`AppLogger`). All log records inherently track contextual fields (like timestamp, level, and logger name), providing an easy integration path for standard log-aggregation platforms (e.g., Datadog, ELK).

### Correlation ID Behavior
To trace requests as they navigate the backend:
- The middleware (`RequestContextMiddleware`) searches for an `X-Request-ID` or `X-Correlation-ID` incoming header.
- If no header is provided, a new UUID is generated.
- This ID is stored in a `contextvars.ContextVar`, automatically injecting the `request_id` into all logs emitted during the lifecycle of the request.
- The `request_id` is then returned in the HTTP response headers under `X-Request-ID`.
- WebSocket connections capture the ID during the handshake, ensuring socket lifecycle events belong to the same correlation boundary.

### Analytics Events Tracked
Business logic flows generate distinct analytics events routed through the standard structured logging output, bypassing the need for a separate high-volume analytics database table. The events currently tracked are:
- `user_registered`: When a new user completes the sign-up flow.
- `ngo_created`: When an NGO profile is initialized.
- `ngo_verified`: When a platform admin approves an NGO.
- `group_created`: When a new group is spawned under an NGO.
- `join_request_submitted`: When a user asks to join a private group.
- `join_request_approved`: When an administrator allows the user into a group.
- `event_created`: When an NGO or Group publishes a new event calendar invite.
- `attachment_uploaded`: When a user attaches media to a channel message.

### Privacy and Sensitive Data Exclusions
To maintain strict compliance and protect user data, explicit filter rules have been added to the logger formats (`SENSITIVE_KEYS`). The following fields are redacted as `***` dynamically before reaching standard output:
- `password`
- `token`
- `access_token`
- `refresh_token`
- `secret`
- `id_token`
- `authorization`
- `device_token`
- `fcm_token`

*Note: Avoid passing raw personal data or sensitive request/response payloads in arbitrary logging `extra` dictionaries.*

### Future Observability Roadmap
1.  **Metrics Integration:** Incorporate Prometheus/OpenTelemetry metrics to capture granular latency and error-rate data.
2.  **Distributed Tracing:** Add Jaeger or standard OpenTelemetry tracing context propagation between microservices/layers.
3.  **Dashboards & Alerting:** Build out Grafana dashboards connecting directly to the structured log ingest, and configure alerts for irregular error rates or authentication drops.

## Project Structure

This monorepo is divided into two primary parts:

1.  **`/flutter_app`**: The frontend mobile application built using [Flutter](https://flutter.dev/). It is designed to be cross-platform, targeting both iOS and Android.
2.  **`/backend`**: The backend service built using Python and [FastAPI](https://fastapi.tiangolo.com/). This handles the core logic, API endpoints, and database interactions for NgoConnect.

## Role Model Overview
The application follows a strict hierarchical Role-Based Access Control (RBAC) model:
- **NGO Scope Roles:** `owner`, `admin`, `member`. An NGO Owner or Admin has cascading privileges over all groups and channels belonging to the NGO.
- **Group Scope Roles:** `group_admin`, `group_moderator`, `member`. These roles dictate permissions specifically within a given group.

## Visibility Rules
- **Groups:** Can be `public` (anyone can join/view) or `invite_only`. A user must be a member of the group, or an admin of the parent NGO, to view an `invite_only` group.
- **Channels:** Reside within groups. Channels inherit group visibility and can be additionally restricted via their own `invite_only` flag.
- **Events:** Only *verified* NGOs can publish `public` events. Non-verified NGOs are restricted to creating `members_only` events.

## Search Architecture
NgoConnect supports first-class PostgreSQL-backed search across NGOs, Groups, and Events.

- **Indexes**: Uses PostgreSQL full-text search `TSVECTOR` and `GIN` indexes.
- **Fields Indexed**:
  - `ngos`: `name`, `about`, `slug`
  - `groups`: `name`, `about`, `slug`
  - `events`: `title`, `description`, `location`
- **Filters Supported**:
  - Visibility (public vs invite-only/private vs members-only)
  - Verification status (only verified NGOs appear in public search)
  - Authorization (search returns groups and events you have access to as an NGO owner/admin or group member)
- **Limitations**:
  - Native PostgreSQL search handles text matching well, but complex typographic corrections or fuzzy matching is limited compared to dedicated search engines like Elasticsearch.
  - SQLite backend uses a simplified `ilike` wildcard fallback matching approach, meaning full-text features like exact string boundaries and ranking are limited during local testing.

## Endpoints

### Search
- `GET /search/ngos` - Search for public, verified NGOs.
- `GET /search/groups` - Search groups you have access to.
- `GET /search/events` - Search events you have access to.

### Auth
- `POST /auth/register` - Register a new user
- `POST /auth/login` - Form-data login (OAuth2 compatible)
- `POST /auth/refresh` - Refresh access tokens
- `POST /auth/google` - Authenticate via Google ID token
- `GET /auth/me` - Get current user profile

### NGOs
- `POST /ngos` - Create an NGO
- `GET /ngos/discover` - List public, verified NGOs
- `GET /ngos/slug/{slug}` - Get NGO details
- `PUT /ngos/{ngo_id}` - Update NGO details (Admin only)
- `POST /ngos/{ngo_id}/verify` - Request verification (Admin only)
- `POST /ngos/{ngo_id}/events` - Create NGO event
- `GET /ngos/{ngo_id}/events` - List NGO events

### Groups
- `POST /ngos/{ngo_id}/groups` - Create a group
- `GET /ngos/{ngo_id}/groups` - List groups under an NGO
- `GET /groups/{group_id}` - Get group details
- `PATCH /groups/{group_id}` - Update group details
- `GET /groups/{group_id}/members` - List group members
- `POST /groups/{group_id}/join-request` - Request to join a group
- `POST /join-requests/{request_id}/approve` - Approve join request

### Channels & Messages
- `POST /groups/{group_id}/channels` - Create a channel (max 5 per group)
- `GET /groups/{group_id}/channels` - List channels
- `POST /channels/{channel_id}/messages` - Send a message
- `GET /channels/{channel_id}/messages` - Retrieve messages
- `WS /ws/channels/{channel_id}?token={access_token}` - WebSocket endpoint for realtime messages

## Testing

### Backend
To run the full backend test suite, which uses an in-memory SQLite database:
```bash
cd backend
PYTHONPATH=. DATABASE_URL="sqlite:///:memory:" pytest app/tests/
```

### Frontend (Flutter)
To validate the Flutter app:
```bash
cd flutter_app
flutter analyze
flutter test
```

## Known Limitations and Next Steps
1. **Group/Channel Deletion:** While models exist, soft-delete or explicit cascading delete endpoints for groups/channels need to be securely exposed.
2. **Role Promotion UI:** The backend supports assigning/removing roles (`/groups/{group_id}/roles/assign`), but the Flutter app requires UI workflows to expose this feature for Group Admins.
3. **Caching:** Highly accessed read endpoints (`/ngos/discover`) would benefit from Redis caching.
4. **Offline Mode:** The Flutter app currently relies completely on live network status. Adding local database caching (e.g. Isar or Hive) for messages and events is recommended.
5. **WebSocket Scaling:** The current realtime messaging uses an in-memory `ConnectionManager`. This works well for single-instance deployments but will not scale horizontally across multiple instances. Future iterations should implement a Redis Pub/Sub backend to synchronize broadcasts across multiple server nodes.

## Storage Architecture

NgoConnect uses a storage adapter pattern to handle file uploads such as message attachments.
- **Local Adapter:** Saves uploaded files to a local directory (e.g. `uploads/`) and serves files via the backend. Used in development environments.
- **S3 Adapter:** Uploads files to an AWS S3-compatible bucket and provides presigned URLs for secure downloads. Used in staging/production environments.

To configure the storage behavior, ensure the following environment variables are set for the backend:
- `STORAGE_BACKEND`: `local` or `s3`
- `LOCAL_STORAGE_DIR`: Directory path for local uploads (e.g., `uploads`)
- `MAX_UPLOAD_SIZE_MB`: Max allowed file size in MB.
- `S3_BUCKET_NAME`, `S3_ENDPOINT_URL`, `S3_ACCESS_KEY`, `S3_SECRET_KEY`, `S3_REGION`: Settings needed for S3 adapter.

For local S3 integration tests, tools like `LocalStack` or `MinIO` are recommended to mock the bucket.

## Getting Started

Please refer to the READMEs in the respective directories for specific instructions on how to set up, run, and test the frontend and backend.

- [Flutter App README](./flutter_app/README.md)
- [Backend README](./backend/README.md)

## Contributing

Please read the `AGENTS.md` file at the root of the repository to understand the coding conventions, project organization, and rules for contributing to this codebase.
