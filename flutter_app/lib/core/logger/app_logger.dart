import 'dart:convert';
import 'dart:developer' as developer;

class AppLogger {
  static const Set<String> _sensitiveKeys = {
    'password',
    'token',
    'access_token',
    'refresh_token',
    'secret',
    'id_token',
    'authorization',
    'device_token',
    'fcm_token',
  };

  static void info(String message, {Map<String, dynamic>? data}) {
    _log('INFO', message, data: data);
  }

  static void debug(String message, {Map<String, dynamic>? data}) {
    _log('DEBUG', message, data: data);
  }

  static void warning(String message, {Map<String, dynamic>? data}) {
    _log('WARN', message, data: data);
  }

  static void error(
    String message, {
    dynamic error,
    StackTrace? stackTrace,
    Map<String, dynamic>? data,
  }) {
    _log('ERROR', message, error: error, stackTrace: stackTrace, data: data);
  }

  static void _log(
    String level,
    String message, {
    dynamic error,
    StackTrace? stackTrace,
    Map<String, dynamic>? data,
  }) {
    Map<String, dynamic>? safeData;
    if (data != null) {
      safeData = _sanitizeData(data);
    }

    developer.log(
      message,
      name: 'NgoConnect',
      level: _getLevel(level),
      error: error,
      stackTrace: stackTrace,
      time: DateTime.now(),
    );

    // If we have extra structured data, output it clearly
    if (safeData != null && safeData.isNotEmpty) {
      developer.log(
        '  └─ Extra: ${jsonEncode(safeData)}',
        name: 'NgoConnect',
        level: _getLevel(level),
      );
    }
  }

  static int _getLevel(String level) {
    switch (level) {
      case 'INFO':
        return 800; // Level.INFO.value
      case 'WARN':
        return 900; // Level.WARNING.value
      case 'ERROR':
        return 1000; // Level.SEVERE.value
      default:
        return 800;
    }
  }

  static Map<String, dynamic> _sanitizeData(Map<String, dynamic> data) {
    final sanitized = <String, dynamic>{};
    for (final entry in data.entries) {
      if (_sensitiveKeys.contains(entry.key.toLowerCase())) {
        sanitized[entry.key] = '***';
      } else if (entry.value is Map<String, dynamic>) {
        sanitized[entry.key] = _sanitizeData(entry.value);
      } else {
        sanitized[entry.key] = entry.value;
      }
    }
    return sanitized;
  }
}
