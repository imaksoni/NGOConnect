import 'package:go_router/go_router.dart';
import '../../features/auth/presentation/screens/login_screen.dart';
import '../../features/auth/presentation/screens/register_screen.dart';
import '../../features/auth/presentation/screens/splash_screen.dart';
import '../../features/auth/presentation/screens/welcome_screen.dart';
import 'route_constants.dart';

final appRouter = GoRouter(
  initialLocation: RouteConstants.splashPath,
  routes: [
    GoRoute(
      path: RouteConstants.splashPath,
      name: RouteConstants.splashName,
      builder: (context, state) => const SplashScreen(),
    ),
    GoRoute(
      path: RouteConstants.welcomePath,
      name: RouteConstants.welcomeName,
      builder: (context, state) => const WelcomeScreen(),
    ),
    GoRoute(
      path: RouteConstants.loginPath,
      name: RouteConstants.loginName,
      builder: (context, state) => const LoginScreen(),
    ),
    GoRoute(
      path: RouteConstants.registerPath,
      name: RouteConstants.registerName,
      builder: (context, state) => const RegisterScreen(),
    ),
  ],
);
