import 'package:go_router/go_router.dart';
import '../../features/auth/presentation/screens/login_screen.dart';
import '../../features/auth/presentation/screens/register_screen.dart';
import '../../features/auth/presentation/screens/splash_screen.dart';
import '../../features/auth/presentation/screens/welcome_screen.dart';
import '../../features/home/presentation/screens/home_screen.dart';
import '../../features/ngo/presentation/screens/ngo_detail_screen.dart';
import '../../features/ngo/presentation/screens/group_list_screen.dart';
import '../../features/ngo/presentation/screens/group_detail_screen.dart';
import '../../features/groups/presentation/screens/join_requests_screen.dart';
import '../../features/channels/presentation/screens/channel_list_screen.dart';
import '../../features/channels/presentation/screens/channel_detail_screen.dart';
import '../../features/events/presentation/screens/event_list_screen.dart';
import '../../features/events/presentation/screens/create_event_screen.dart';
import '../../features/admin/presentation/screens/admin_dashboard_screen.dart';
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
    GoRoute(
      path: RouteConstants.joinRequestsPath,
      name: RouteConstants.joinRequestsName,
      builder: (context, state) {
        final groupId = state.pathParameters['groupId']!;
        return JoinRequestsScreen(groupId: groupId);
      },
    ),
    GoRoute(
      path: RouteConstants.channelListPath,
      name: RouteConstants.channelListName,
      builder: (context, state) {
        final groupId = state.pathParameters['groupId']!;
        return ChannelListScreen(groupId: groupId);
      },
    ),
    GoRoute(
      path: RouteConstants.channelDetailPath,
      name: RouteConstants.channelDetailName,
      builder: (context, state) {
        final channelId = state.pathParameters['channelId']!;
        return ChannelDetailScreen(channelId: channelId);
      },
    ),
    GoRoute(
      path: RouteConstants.ngoEventsPath,
      name: RouteConstants.ngoEventsName,
      builder: (context, state) {
        final ngoId = state.pathParameters['ngoId']!;
        return EventListScreen(ngoId: ngoId);
      },
    ),
    GoRoute(
      path: RouteConstants.createNgoEventPath,
      name: RouteConstants.createNgoEventName,
      builder: (context, state) {
        final ngoId = state.pathParameters['ngoId']!;
        return CreateEventScreen(ngoId: ngoId);
      },
    ),
    GoRoute(
      path: RouteConstants.groupEventsPath,
      name: RouteConstants.groupEventsName,
      builder: (context, state) {
        final groupId = state.pathParameters['groupId']!;
        return EventListScreen(groupId: groupId);
      },
    ),
    GoRoute(
      path: RouteConstants.createGroupEventPath,
      name: RouteConstants.createGroupEventName,
      builder: (context, state) {
        final groupId = state.pathParameters['groupId']!;
        return CreateEventScreen(groupId: groupId);
      },
    ),
    GoRoute(
      path: RouteConstants.adminDashboardPath,
      name: RouteConstants.adminDashboardName,
      builder: (context, state) => const AdminDashboardScreen(),
    ),
  ],
);
