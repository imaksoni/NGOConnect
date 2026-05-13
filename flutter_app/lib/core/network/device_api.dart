import 'package:dio/dio.dart';
import 'dart:io' show Platform;
import 'package:flutter/foundation.dart' show kIsWeb, debugPrint;
import 'api_client.dart';

class DeviceApi {
  final ApiClient _apiClient;

  DeviceApi({required ApiClient apiClient}) : _apiClient = apiClient;

  Future<void> registerDeviceToken(String token) async {
    try {
      String platform = 'unknown';
      if (kIsWeb) {
        platform = 'web';
      } else if (Platform.isAndroid) {
        platform = 'android';
      } else if (Platform.isIOS) {
        platform = 'ios';
      }

      await _apiClient.dio.post(
        '/devices/register',
        data: {'device_token': token, 'platform': platform},
      );
    } on DioException catch (e) {
      // Don't crash auth flow if device registration fails
      debugPrint('Failed to register device token: $e');
    }
  }

  Future<void> unregisterDeviceToken(String token) async {
    try {
      await _apiClient.dio.post(
        '/devices/unregister',
        data: {'device_token': token},
      );
    } on DioException catch (e) {
      debugPrint('Failed to unregister device token: $e');
    }
  }
}
