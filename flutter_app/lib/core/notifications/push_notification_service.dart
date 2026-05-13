import 'package:firebase_core/firebase_core.dart';
import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:flutter/foundation.dart';
import '../network/device_api.dart';

Future<void> _firebaseMessagingBackgroundHandler(RemoteMessage message) async {
  await Firebase.initializeApp();
  debugPrint("Handling a background message: ${message.messageId}");
}

class PushNotificationService {
  final FirebaseMessaging _firebaseMessaging = FirebaseMessaging.instance;
  DeviceApi? _deviceApi;

  void setDeviceApi(DeviceApi api) {
    _deviceApi = api;
  }

  Future<void> initialize() async {
    try {
      await Firebase.initializeApp();

      FirebaseMessaging.onBackgroundMessage(_firebaseMessagingBackgroundHandler);

      // Listen for token refreshes
      _firebaseMessaging.onTokenRefresh.listen((newToken) {
        debugPrint("FCM Token Refreshed: $newToken");
        _deviceApi?.registerDeviceToken(newToken);
      });

      FirebaseMessaging.onMessage.listen((RemoteMessage message) {
        debugPrint('Got a message whilst in the foreground!');
        if (message.notification != null) {
          debugPrint('Message also contained a notification: ${message.notification?.title}');
        }
      });

    } catch (e) {
      debugPrint("Firebase initialization failed or not configured: $e");
    }
  }

  Future<bool> requestPermissions() async {
    try {
      NotificationSettings settings = await _firebaseMessaging.requestPermission(
        alert: true,
        announcement: false,
        badge: true,
        carPlay: false,
        criticalAlert: false,
        provisional: false,
        sound: true,
      );

      return settings.authorizationStatus == AuthorizationStatus.authorized;
    } catch (e) {
      debugPrint("Failed to request permissions: $e");
      return false;
    }
  }

  Future<String?> getToken() async {
    try {
      if (kIsWeb) {
        return null;
      }
      return await _firebaseMessaging.getToken();
    } catch (e) {
      debugPrint("Failed to get FCM token: $e");
      return null;
    }
  }
}
