import sys

def update_router():
    with open('flutter_app/lib/core/router/app_router.dart', 'r') as f:
        content = f.read()

    imports = """import '../../features/channels/presentation/screens/channel_detail_screen.dart';
import '../../features/events/presentation/screens/event_list_screen.dart';
import '../../features/events/presentation/screens/create_event_screen.dart';
import 'route_constants.dart';"""
    content = content.replace("import '../../features/channels/presentation/screens/channel_detail_screen.dart';\nimport 'route_constants.dart';", imports)

    routes = """    GoRoute(
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
    ),"""
    content = content.replace("""    GoRoute(
      path: RouteConstants.channelDetailPath,
      name: RouteConstants.channelDetailName,
      builder: (context, state) {
        final channelId = state.pathParameters['channelId']!;
        return ChannelDetailScreen(channelId: channelId);
      },
    ),""", routes)

    with open('flutter_app/lib/core/router/app_router.dart', 'w') as f:
        f.write(content)

update_router()
