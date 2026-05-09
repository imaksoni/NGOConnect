import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../data/models/notification_model.dart';
import '../../data/repositories/notification_repository.dart';

final notificationProvider =
    AsyncNotifierProvider<NotificationNotifier, List<NotificationModel>>(() {
      return NotificationNotifier();
    });

class NotificationNotifier extends AsyncNotifier<List<NotificationModel>> {
  @override
  Future<List<NotificationModel>> build() async {
    return _fetchNotifications();
  }

  Future<List<NotificationModel>> _fetchNotifications() async {
    return await notificationRepository.getNotifications();
  }

  Future<void> refresh() async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() => _fetchNotifications());
  }

  Future<void> markAsRead(String id) async {
    try {
      await notificationRepository.markAsRead(id);

      // Update state locally
      final currentList = state.value ?? [];
      final updatedList = currentList.map((notif) {
        if (notif.id == id) {
          return NotificationModel(
            id: notif.id,
            userId: notif.userId,
            type: notif.type,
            title: notif.title,
            body: notif.body,
            isRead: true,
            entityType: notif.entityType,
            entityId: notif.entityId,
            createdAt: notif.createdAt,
          );
        }
        return notif;
      }).toList();

      state = AsyncValue.data(updatedList);
    } catch (e, st) {
      state = AsyncValue.error(e, st);
    }
  }

  Future<void> markAllAsRead() async {
    try {
      await notificationRepository.markAllAsRead();

      // Update state locally
      final currentList = state.value ?? [];
      final updatedList = currentList.map((notif) {
        return NotificationModel(
          id: notif.id,
          userId: notif.userId,
          type: notif.type,
          title: notif.title,
          body: notif.body,
          isRead: true,
          entityType: notif.entityType,
          entityId: notif.entityId,
          createdAt: notif.createdAt,
        );
      }).toList();

      state = AsyncValue.data(updatedList);
    } catch (e, st) {
      state = AsyncValue.error(e, st);
    }
  }
}

final unreadNotificationsCountProvider = Provider<int>((ref) {
  final notifications = ref.watch(notificationProvider).value ?? [];
  return notifications.where((n) => !n.isRead).length;
});
