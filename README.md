# NgoConnect

Welcome to the NgoConnect project! This repository uses a monorepo structure containing both the mobile application and the backend service.

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

## Endpoints

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

## Getting Started

Please refer to the READMEs in the respective directories for specific instructions on how to set up, run, and test the frontend and backend.

- [Flutter App README](./flutter_app/README.md)
- [Backend README](./backend/README.md)

## Contributing

Please read the `AGENTS.md` file at the root of the repository to understand the coding conventions, project organization, and rules for contributing to this codebase.
