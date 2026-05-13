import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:google_sign_in/google_sign_in.dart';
import '../../../../core/network/api_client.dart';
import '../../data/models/user_model.dart';
import '../../data/repositories/auth_repository.dart';
import '../../data/repositories/token_repository.dart';
import '../../../../core/network/device_api.dart';
import '../../../../core/notifications/push_notification_service.dart';

final tokenRepositoryProvider = Provider<TokenRepository>((ref) {
  return TokenRepository();
});

final apiClientProvider = Provider<ApiClient>((ref) {
  final tokenRepository = ref.watch(tokenRepositoryProvider);
  return ApiClient(tokenRepository: tokenRepository);
});

final authRepositoryProvider = Provider<AuthRepository>((ref) {
  final apiClient = ref.watch(apiClientProvider);
  final tokenRepository = ref.watch(tokenRepositoryProvider);

  final authRepository = AuthRepository(
    apiClient: apiClient,
    tokenRepository: tokenRepository,
  );

  apiClient.setAuthRepository(authRepository);
  return authRepository;
});

final pushNotificationServiceProvider = Provider<PushNotificationService>((
  ref,
) {
  return PushNotificationService();
});

final deviceApiProvider = Provider<DeviceApi>((ref) {
  final apiClient = ref.watch(apiClientProvider);
  return DeviceApi(apiClient: apiClient);
});

final authProvider = NotifierProvider<AuthNotifier, AsyncValue<UserModel?>>(
  AuthNotifier.new,
);

class AuthNotifier extends Notifier<AsyncValue<UserModel?>> {
  late final AuthRepository _authRepository;
  late final PushNotificationService _pushNotificationService;
  late final DeviceApi _deviceApi;
  String? _fcmToken;

  @override
  AsyncValue<UserModel?> build() {
    _authRepository = ref.watch(authRepositoryProvider);
    _pushNotificationService = ref.watch(pushNotificationServiceProvider);
    _deviceApi = ref.watch(deviceApiProvider);
    _pushNotificationService.setDeviceApi(_deviceApi);
    _pushNotificationService.initialize();
    checkAuthStatus();
    return const AsyncValue.loading();
  }

  Future<void> _registerDeviceToken() async {
    final granted = await _pushNotificationService.requestPermissions();
    if (granted) {
      _fcmToken = await _pushNotificationService.getToken();
      if (_fcmToken != null) {
        await _deviceApi.registerDeviceToken(_fcmToken!);
      }
    }
  }

  Future<void> _unregisterDeviceToken() async {
    if (_fcmToken != null) {
      await _deviceApi.unregisterDeviceToken(_fcmToken!);
      _fcmToken = null;
    }
  }

  Future<void> checkAuthStatus() async {
    state = const AsyncValue.loading();
    try {
      final user = await _authRepository.getMe();
      state = AsyncValue.data(user);
      if (user != null) {
        await _registerDeviceToken();
      }
    } catch (e, stack) {
      state = AsyncValue.error(e, stack);
    }
  }

  Future<void> login(String email, String password) async {
    state = const AsyncValue.loading();
    try {
      await _authRepository.login(email: email, password: password);
      await checkAuthStatus();
    } catch (e, stack) {
      state = AsyncValue.error(e, stack);
      rethrow;
    }
  }

  Future<void> signInWithGoogle() async {
    state = const AsyncValue.loading();
    try {
      final GoogleSignIn googleSignIn = GoogleSignIn();

      final googleUser = await googleSignIn.signIn();

      if (googleUser == null) {
        // User cancelled the sign-in flow
        state = const AsyncValue.data(null);
        return;
      }

      final googleAuth = await googleUser.authentication;
      final String? idToken = googleAuth.idToken;

      if (idToken == null) {
        throw Exception('Failed to get Google ID token');
      }

      await _authRepository.loginWithGoogle(idToken: idToken);
      await checkAuthStatus();
    } catch (e, stack) {
      state = AsyncValue.error(e, stack);
      rethrow;
    }
  }

  Future<void> register(
    String email,
    String password, {
    String? firstName,
    String? lastName,
  }) async {
    state = const AsyncValue.loading();
    try {
      await _authRepository.register(
        email: email,
        password: password,
        firstName: firstName,
        lastName: lastName,
      );
      // Automatically login after successful registration
      await login(email, password);
    } catch (e, stack) {
      state = AsyncValue.error(e, stack);
      rethrow;
    }
  }

  Future<void> logout() async {
    state = const AsyncValue.loading();
    try {
      await _unregisterDeviceToken();
      await _authRepository.logout();
      state = const AsyncValue.data(null);
    } catch (e, stack) {
      state = AsyncValue.error(e, stack);
    }
  }
}
