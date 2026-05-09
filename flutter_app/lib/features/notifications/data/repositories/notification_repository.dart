import '../../../../core/network/api_client.dart';
import '../models/notification_model.dart';

class NotificationRepository {
  final ApiClient _apiClient = ApiClient();

  Future<List<NotificationModel>> getNotifications() async {
    final response = await _apiClient.dio.get('/notifications');
    final List<dynamic> data = response.data;
    return data.map((json) => NotificationModel.fromJson(json)).toList();
  }

  Future<NotificationModel> markAsRead(String notificationId) async {
    final response = await _apiClient.dio.post(
      '/notifications/$notificationId/read',
    );
    return NotificationModel.fromJson(response.data);
  }

  Future<void> markAllAsRead() async {
    await _apiClient.dio.post('/notifications/read-all');
  }
}

final notificationRepository = NotificationRepository();
