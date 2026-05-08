import 'package:go_router/go_router.dart';
import '../../features/auth/presentation/screens/login_screen.dart';
import '../../features/auth/presentation/screens/register_screen.dart';
import '../../features/auth/presentation/screens/splash_screen.dart';
import '../../features/auth/presentation/screens/welcome_screen.dart';
import '../../features/home/presentation/screens/home_screen.dart';
import '../../features/ngo/presentation/screens/ngo_detail_screen.dart';
import '../../features/ngo/presentation/screens/group_list_screen.dart';
import '../../features/ngo/presentation/screens/group_detail_screen.dart';
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
    GoRoute(
      path: RouteConstants.homePath,
      name: RouteConstants.homeName,
      builder: (context, state) => const HomeScreen(),
    ),
    GoRoute(
      path: RouteConstants.ngoDetailPath,
      name: RouteConstants.ngoDetailName,
      builder: (context, state) {
        final slug = state.pathParameters['slug']!;
        return NgoDetailScreen(slug: slug);
      },
    ),
    GoRoute(
      path: RouteConstants.groupListPath,
      name: RouteConstants.groupListName,
      builder: (context, state) {
        final ngoId = state.pathParameters['ngoId']!;
        return GroupListScreen(ngoId: ngoId);
      },
    ),
    GoRoute(
      path: RouteConstants.groupDetailPath,
      name: RouteConstants.groupDetailName,
      builder: (context, state) {
        final groupId = state.pathParameters['groupId']!;
        return GroupDetailScreen(groupId: groupId);
      },
    ),
  ],
);
