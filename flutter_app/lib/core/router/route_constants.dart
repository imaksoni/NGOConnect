class RouteConstants {
  static const String splashPath = '/';
  static const String splashName = 'splash';

  static const String welcomePath = '/welcome';
  static const String welcomeName = 'welcome';

  static const String loginPath = '/login';
  static const String loginName = 'login';

  static const String registerPath = '/register';
  static const String registerName = 'register';

  static const String homePath = '/home';
  static const String homeName = 'home';

  static const String ngoDetailPath = '/ngo/:slug';
  static const String ngoDetailName = 'ngo_detail';

  static const String groupListPath = '/ngo/:ngoId/groups';
  static const String groupListName = 'groupList';
  static const String groupDetailPath = '/groups/:groupId';
  static const String groupDetailName = 'groupDetail';
  static const String joinRequestsPath = '/groups/:groupId/join-requests';
  static const String joinRequestsName = 'joinRequests';

  static const String channelListPath = '/groups/:groupId/channels';
  static const String channelListName = 'channelList';
  static const String channelDetailPath = '/channels/:channelId';
  static const String channelDetailName = 'channelDetail';

  static const String ngoEventsPath = '/ngos/:ngoId/events';
  static const String ngoEventsName = 'ngoEvents';
  static const String createNgoEventPath = '/ngos/:ngoId/events/create';
  static const String createNgoEventName = 'createNgoEvent';

  static const String groupEventsPath = '/groups/:groupId/events';
  static const String groupEventsName = 'groupEvents';
  static const String createGroupEventPath = '/groups/:groupId/events/create';
  static const String createGroupEventName = 'createGroupEvent';
}
