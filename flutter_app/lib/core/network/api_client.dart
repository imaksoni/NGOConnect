import 'package:dio/dio.dart';
import '../../features/auth/data/repositories/token_repository.dart';
import '../../features/auth/data/repositories/auth_repository.dart';
import '../logger/app_logger.dart';

class ApiClient {
  late final Dio _dio;
  final TokenRepository _tokenRepository;
  AuthRepository?
  _authRepository; // Injected later to avoid circular dependency during setup

  ApiClient({String? baseUrl, TokenRepository? tokenRepository})
    : _tokenRepository = tokenRepository ?? TokenRepository() {
    _dio = Dio(
      BaseOptions(
        baseUrl: baseUrl ?? 'http://10.0.2.2:8000', // Default backend URL
        connectTimeout: const Duration(seconds: 10),
        receiveTimeout: const Duration(seconds: 10),
        responseType: ResponseType.json,
      ),
    );

    _dio.interceptors.add(
      InterceptorsWrapper(
        onRequest: (options, handler) async {
          final accessToken = await _tokenRepository.getAccessToken();
          if (accessToken != null) {
            options.headers['Authorization'] = 'Bearer $accessToken';
          }
          return handler.next(options);
        },
        onResponse: (response, handler) {
          return handler.next(response);
        },
        onError: (DioException e, handler) async {
          AppLogger.error(
            'API Error: ${e.message}',
            error: e,
            stackTrace: e.stackTrace,
            data: {
              'path': e.requestOptions.path,
              'method': e.requestOptions.method,
              'statusCode': e.response?.statusCode,
              'headers': e.requestOptions.headers,
            },
          );

          if (e.response?.statusCode == 401 && _authRepository != null) {
            // Check if request was already a refresh attempt to avoid infinite loops
            if (e.requestOptions.path != '/auth/refresh') {
              final refreshed = await _authRepository!.refresh();
              if (refreshed) {
                // Retry original request
                final options = e.requestOptions;
                final newToken = await _tokenRepository.getAccessToken();
                if (newToken != null) {
                  options.headers['Authorization'] = 'Bearer $newToken';
                }
                try {
                  final response = await _dio.fetch(options);
                  return handler.resolve(response);
                } on DioException catch (retryError) {
                  return handler.next(retryError);
                }
              }
            }
          }
          return handler.next(e);
        },
      ),
    );
  }

  Dio get dio => _dio;

  void setAuthRepository(AuthRepository authRepository) {
    _authRepository = authRepository;
  }
}
