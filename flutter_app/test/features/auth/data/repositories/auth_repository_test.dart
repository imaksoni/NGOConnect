import 'package:dio/dio.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:ngo_connect/core/network/api_client.dart';
import 'package:ngo_connect/features/auth/data/repositories/auth_repository.dart';
import 'package:ngo_connect/features/auth/data/repositories/token_repository.dart';

class MockApiClient extends Mock implements ApiClient {}

class MockDio extends Mock implements Dio {}

class MockTokenRepository extends Mock implements TokenRepository {}

void main() {
  late AuthRepository authRepository;
  late MockApiClient mockApiClient;
  late MockDio mockDio;
  late MockTokenRepository mockTokenRepository;

  setUp(() {
    mockApiClient = MockApiClient();
    mockDio = MockDio();
    mockTokenRepository = MockTokenRepository();

    when(() => mockApiClient.dio).thenReturn(mockDio);

    authRepository = AuthRepository(
      apiClient: mockApiClient,
      tokenRepository: mockTokenRepository,
    );
  });

  group('AuthRepository', () {
    const testEmail = 'test@example.com';
    const testPassword = 'password123';

    test('login success saves tokens', () async {
      final mockResponse = Response(
        requestOptions: RequestOptions(path: '/auth/login'),
        data: {
          'access_token': 'access_token_123',
          'refresh_token': 'refresh_token_123',
          'token_type': 'bearer',
        },
      );

      when(
        () => mockDio.post(any(), data: any(named: 'data')),
      ).thenAnswer((_) async => mockResponse);

      when(
        () => mockTokenRepository.saveTokens(
          accessToken: any(named: 'accessToken'),
          refreshToken: any(named: 'refreshToken'),
        ),
      ).thenAnswer((_) async {});

      await authRepository.login(email: testEmail, password: testPassword);

      verify(
        () => mockDio.post('/auth/login', data: any(named: 'data')),
      ).called(1);

      verify(
        () => mockTokenRepository.saveTokens(
          accessToken: 'access_token_123',
          refreshToken: 'refresh_token_123',
        ),
      ).called(1);
    });

    test('login failure throws Exception', () async {
      when(() => mockDio.post(any(), data: any(named: 'data'))).thenThrow(
        DioException(
          requestOptions: RequestOptions(path: '/auth/login'),
          response: Response(
            requestOptions: RequestOptions(path: '/auth/login'),
            data: {'detail': 'Incorrect email or password'},
          ),
        ),
      );

      expect(
        () => authRepository.login(email: testEmail, password: testPassword),
        throwsA(
          isA<Exception>().having(
            (e) => e.toString(),
            'message',
            contains('Incorrect email or password'),
          ),
        ),
      );
    });

    test('refresh success saves new tokens', () async {
      when(
        () => mockTokenRepository.getRefreshToken(),
      ).thenAnswer((_) async => 'old_refresh_token');

      final mockResponse = Response(
        requestOptions: RequestOptions(path: '/auth/refresh'),
        data: {
          'access_token': 'new_access_token',
          'refresh_token': 'new_refresh_token',
          'token_type': 'bearer',
        },
      );

      when(
        () => mockDio.post(any(), data: any(named: 'data')),
      ).thenAnswer((_) async => mockResponse);

      when(
        () => mockTokenRepository.saveTokens(
          accessToken: any(named: 'accessToken'),
          refreshToken: any(named: 'refreshToken'),
        ),
      ).thenAnswer((_) async {});

      final result = await authRepository.refresh();

      expect(result, isTrue);
      verify(
        () => mockTokenRepository.saveTokens(
          accessToken: 'new_access_token',
          refreshToken: 'new_refresh_token',
        ),
      ).called(1);
    });

    test('refresh failure returns false and logs out', () async {
      when(
        () => mockTokenRepository.getRefreshToken(),
      ).thenAnswer((_) async => 'old_refresh_token');

      when(() => mockDio.post(any(), data: any(named: 'data'))).thenThrow(
        DioException(requestOptions: RequestOptions(path: '/auth/refresh')),
      );

      when(() => mockTokenRepository.clearTokens()).thenAnswer((_) async {});

      final result = await authRepository.refresh();

      expect(result, isFalse);
      verify(() => mockTokenRepository.clearTokens()).called(1);
    });
  });
}
