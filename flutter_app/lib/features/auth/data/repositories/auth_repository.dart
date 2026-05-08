import 'package:dio/dio.dart';
import '../../../../core/network/api_client.dart';
import '../models/user_model.dart';
import '../models/token_model.dart';
import 'token_repository.dart';

class AuthRepository {
  final ApiClient _apiClient;
  final TokenRepository _tokenRepository;

  AuthRepository({
    required ApiClient apiClient,
    required TokenRepository tokenRepository,
  })  : _apiClient = apiClient,
        _tokenRepository = tokenRepository;

  Future<UserModel> register({
    required String email,
    required String password,
    String? firstName,
    String? lastName,
  }) async {
    try {
      final response = await _apiClient.dio.post(
        '/auth/register',
        data: {
          'email': email,
          'password': password,
          'first_name': firstName,
          'last_name': lastName,
        }..removeWhere((key, value) => value == null),
      );
      return UserModel.fromJson(response.data);
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  Future<void> login({
    required String email,
    required String password,
  }) async {
    try {
      final response = await _apiClient.dio.post(
        '/auth/login',
        data: FormData.fromMap({
          'username': email,
          'password': password,
        }),
      );

      final token = TokenModel.fromJson(response.data);
      await _tokenRepository.saveTokens(
        accessToken: token.accessToken,
        refreshToken: token.refreshToken,
      );
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  Future<bool> refresh() async {
    try {
      final refreshToken = await _tokenRepository.getRefreshToken();
      if (refreshToken == null) {
        return false;
      }

      final response = await _apiClient.dio.post(
        '/auth/refresh',
        data: {
          'refresh_token': refreshToken,
        },
      );

      final token = TokenModel.fromJson(response.data);
      await _tokenRepository.saveTokens(
        accessToken: token.accessToken,
        refreshToken: token.refreshToken,
      );
      return true;
    } catch (_) {
      await logout();
      return false;
    }
  }

  Future<UserModel?> getMe() async {
    try {
      final response = await _apiClient.dio.get('/auth/me');
      return UserModel.fromJson(response.data);
    } catch (_) {
      return null;
    }
  }

  Future<void> logout() async {
    await _tokenRepository.clearTokens();
  }

  Exception _handleError(DioException e) {
    if (e.response?.data != null && e.response?.data is Map) {
      final detail = e.response?.data['detail'];
      if (detail != null && detail is String) {
        return Exception(detail);
      } else if (detail != null && detail is List && detail.isNotEmpty) {
         return Exception(detail[0]['msg'] ?? 'Validation error');
      }
    }
    return Exception(e.message ?? 'An unknown error occurred');
  }
}
