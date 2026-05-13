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

## Authentication

The app supports Email/Password authentication as well as Google Sign-In, interacting directly with the `NgoConnect` backend.

### End-to-End Google Login Flow

1. The user taps the "Sign in with Google" button on the Login or Register screen.
2. The app uses the `google_sign_in` package to prompt the device's native Google Sign-In flow.
3. Upon successful device-side authentication, the app retrieves the Google `id_token`.
4. The app sends this `id_token` to the backend's `/auth/google` endpoint via a POST request.
5. The backend verifies the token with Google, extracts the user's information, and links it to an existing or new user account.
6. The backend returns its own JWT access and refresh tokens.
7. The Flutter app securely stores these tokens using `flutter_secure_storage` and automatically logs the user in, updating the Riverpod `AuthNotifier` state.

### Required Manual Setup for Google Sign-In

For Google Sign-In to function properly on actual devices, you must perform platform-specific configuration in the Google Cloud Console and within the app's platform folders.

**Android:**
1. In the Google Cloud Console, create an OAuth 2.0 Client ID for Android.
2. You will need to provide the package name (e.g., `com.example.ngo_connect`) and the SHA-1 certificate fingerprint of your keystore (either the debug keystore for development or the release keystore for production).
3. Google Sign-In on Android typically doesn't require extra configuration files in the flutter project if the application ID matches the one configured in Google Cloud Console.

**iOS:**
1. In the Google Cloud Console, create an OAuth 2.0 Client ID for iOS.
2. Provide your app's bundle identifier.
3. Download the provided `GoogleService-Info.plist` (or take note of the `CLIENT_ID` and `REVERSED_CLIENT_ID`).
4. Update `flutter_app/ios/Runner/Info.plist` by adding the reversed client ID to your URL types:
   ```xml
   <key>CFBundleURLTypes</key>
   <array>
	<dict>
		<key>CFBundleTypeRole</key>
		<string>Editor</string>
		<key>CFBundleURLSchemes</key>
		<array>
			<!-- Replace this value with the REVERSED_CLIENT_ID -->
			<string>com.googleusercontent.apps.YOUR-CLIENT-ID</string>
		</array>
	</dict>
   </array>
   ```

## Notes
- The authentication flow (Splash, Welcome, Login, Register) is fully functional and uses Riverpod for state management, `dio` for API calls, and `flutter_secure_storage` for token persistence.

## Push Notifications (MVP)

The app integrates `firebase_messaging` to receive FCM push notifications triggered by important backend events.

**Android Setup Requirements:**
- Download your `google-services.json` from the Firebase Console.
- Place it in `android/app/google-services.json`.

**iOS Setup Requirements:**
- Download your `GoogleService-Info.plist` from the Firebase Console.
- Place it in `ios/Runner/GoogleService-Info.plist`.
- Ensure **Push Notifications** and **Background Modes (Remote Notifications)** capabilities are enabled in Xcode.
- A valid APNs key must be uploaded to Firebase for iOS delivery.

**Flow Summary:**
- On successful login or app startup (if already logged in), the app requests notification permissions.
- If granted, the app retrieves the FCM device token and registers it with the backend via `POST /devices/register`.
- On logout, the app explicitly calls `POST /devices/unregister` to stop receiving notifications on that device.
- Deep linking from notifications is currently not supported in the MVP.

**Duplicate Token Registration:**
- If the same FCM token is registered by a different user account on the same device, backend logic reassigns the token to the newly logged-in user to prevent notification bleeding across accounts.

**Refresh Token Handling:**
- The `PushNotificationService` listens to the `FirebaseMessaging.instance.onTokenRefresh` stream. If a token refresh occurs while the user is authenticated, the updated token is automatically re-registered with the backend via `DeviceApi`.
