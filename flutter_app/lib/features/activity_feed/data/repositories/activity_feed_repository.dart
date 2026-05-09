import '../../../../core/network/api_client.dart';
import '../models/activity_log_model.dart';

class ActivityFeedRepository {
  final ApiClient _apiClient = ApiClient();

  Future<List<ActivityLogModel>> getGlobalFeed() async {
    final response = await _apiClient.dio.get('/activity-feed');
    final List<dynamic> data = response.data;
    return data.map((json) => ActivityLogModel.fromJson(json)).toList();
  }

  Future<List<ActivityLogModel>> getNgoFeed(String ngoId) async {
    final response = await _apiClient.dio.get('/ngos/$ngoId/activity-feed');
    final List<dynamic> data = response.data;
    return data.map((json) => ActivityLogModel.fromJson(json)).toList();
  }

  Future<List<ActivityLogModel>> getGroupFeed(String groupId) async {
    final response = await _apiClient.dio.get('/groups/$groupId/activity-feed');
    final List<dynamic> data = response.data;
    return data.map((json) => ActivityLogModel.fromJson(json)).toList();
  }
}

final activityFeedRepository = ActivityFeedRepository();
