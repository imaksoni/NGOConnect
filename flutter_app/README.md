# NgoConnect Flutter App

This is the Flutter mobile application frontend for NgoConnect.

## Getting Started

### Prerequisites
- [Flutter SDK](https://docs.flutter.dev/get-started/install) (version matching environment in pubspec.yaml)
- A connected device or running emulator/simulator.

### Installation

1. Navigate to the `flutter_app` directory:
   ```bash
   cd flutter_app
   ```
2. Get dependencies:
   ```bash
   flutter pub get
   ```

### Running the App

To run the app, simply execute:
```bash
flutter run
```

## Architecture & Structure

The app follows a feature-first architectural pattern to maintain modularity and scalability.

```
lib/
├── core/            # App-wide configurations, constants, network (Dio), router (GoRouter), theme.
├── features/        # Feature modules containing their respective presentation, application, and data layers.
│   ├── auth/        # Authentication module (Splash, Welcome, Login, Register).
│   ├── channels/    # (Scaffolded placeholder)
│   ├── discover/    # (Scaffolded placeholder)
│   ├── events/      # (Scaffolded placeholder)
│   ├── groups/      # (Scaffolded placeholder)
│   └── ngo/         # (Scaffolded placeholder)
├── shared/          # Shared widgets and extensions utilized across features.
└── main.dart        # Entry point wrapping the app with ProviderScope and GoRouter.
```

### Dependencies
- **flutter_riverpod**: State management.
- **go_router**: Declarative routing.
- **dio**: HTTP client abstraction.
- **shared_preferences**: Local data storage (e.g., auth tokens).

## Notes
- Currently, the authentication flow (Splash, Welcome, Login, Register) is **scaffolded** mainly for UI and navigation. The business logic connecting to the actual backend API remains to be implemented.
