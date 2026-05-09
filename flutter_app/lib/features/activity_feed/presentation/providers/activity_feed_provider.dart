import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../data/models/activity_log_model.dart';
import '../../data/repositories/activity_feed_repository.dart';

final globalActivityFeedProvider = FutureProvider<List<ActivityLogModel>>((
  ref,
) async {
  return await activityFeedRepository.getGlobalFeed();
});

final ngoActivityFeedProvider =
    FutureProvider.family<List<ActivityLogModel>, String>((ref, ngoId) async {
      return await activityFeedRepository.getNgoFeed(ngoId);
    });

final groupActivityFeedProvider =
    FutureProvider.family<List<ActivityLogModel>, String>((ref, groupId) async {
      return await activityFeedRepository.getGroupFeed(groupId);
    });
