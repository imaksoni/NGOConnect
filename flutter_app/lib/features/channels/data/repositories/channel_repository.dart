import '../../../../core/network/api_client.dart';
import '../models/channel_model.dart';

class ChannelRepository {
  final ApiClient _apiClient;

  ChannelRepository({required ApiClient apiClient}) : _apiClient = apiClient;

  Future<List<ChannelModel>> getChannelsByGroup(String groupId) async {
    final response = await _apiClient.dio.get('/groups/$groupId/channels');
    final List<dynamic> data = response.data;
    return data.map((json) => ChannelModel.fromJson(json)).toList();
  }

  Future<ChannelModel> getChannel(String channelId) async {
    final response = await _apiClient.dio.get('/channels/$channelId');
    return ChannelModel.fromJson(response.data);
  }
}
