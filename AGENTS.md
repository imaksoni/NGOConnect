# Project Agents and Guidelines

This file outlines the rules, conventions, and architectural guidelines for contributing to the NgoConnect monorepo. Agents and human developers alike should strictly follow these instructions to maintain a clean, consistent, and scalable codebase.

## 1. Directory Purpose

*   **`/backend`**: Contains all backend-related code, specifically a Python FastAPI application. No frontend code should reside here.
*   **`/flutter_app`**: Contains all frontend-related code, specifically a Dart Flutter application. No backend code should reside here.
*   **Root Directory (`/`)**: Should only contain project-wide configuration files (e.g., `.gitignore`, `.editorconfig`), high-level documentation (`README.md`, `AGENTS.md`), and scripts relevant to the entire monorepo. Do not place business logic or application-specific files in the root.

## 2. Modularity & File Size

*   **Avoid Giant Files**: Keep files small and focused on a single responsibility. If a file starts growing beyond 300-400 lines, carefully consider if it should be refactored into smaller, more specific modules.
*   **Modular Design**: Break down complex features into reusable components, functions, or classes.
*   **Separation of Concerns**: Ensure UI logic, business logic, and data access logic are kept separate (e.g., in the backend, separate routers, services, and models).

## 3. Naming Rules

### Python (Backend)
*   **Files & Directories**: `snake_case` (e.g., `user_service.py`, `auth_router.py`).
*   **Classes**: `PascalCase` (e.g., `UserModel`, `DatabaseConfig`).
*   **Functions & Variables**: `snake_case` (e.g., `get_user_by_id`, `is_active`).
*   **Constants**: `UPPER_SNAKE_CASE` (e.g., `MAX_RETRY_COUNT`).

### Dart (Flutter Frontend)
*   **Files & Directories**: `snake_case` (e.g., `login_screen.dart`, `user_repository.dart`).
*   **Classes, Enums, Typedefs**: `PascalCase` (e.g., `LoginScreen`, `UserRole`).
*   **Functions & Variables**: `camelCase` (e.g., `fetchUserData`, `isLoading`).
*   **Constants**: `lowerCamelCase` or `UPPER_SNAKE_CASE` (follow standard Dart conventions, `lowerCamelCase` preferred for constant variables).

## 4. Coding Conventions

*   **Formatting**: Respect the rules defined in the `.editorconfig` file. Ensure files use correct indentation (e.g., 4 spaces for Python, 2 spaces for Dart/JSON/YAML).
*   **Types**:
    *   **Python**: Use type hints extensively (e.g., `def get_user(user_id: int) -> User:`).
    *   **Dart**: Use strong typing. Avoid `dynamic` unless absolutely necessary.
*   **Documentation**: Write meaningful docstrings for classes and functions, especially for public APIs or complex logic. Use standard documentation comments (`///` in Dart, `"""` in Python).
