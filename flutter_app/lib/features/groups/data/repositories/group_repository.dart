import '../../../../core/network/api_client.dart';
import '../../../ngo/data/models/group_model.dart';

class GroupRepository {
  final ApiClient _apiClient;

  GroupRepository({required ApiClient apiClient}) : _apiClient = apiClient;

  Future<List<GroupMemberModel>> getGroupMembers(String groupId) async {
    final response = await _apiClient.dio.get('/groups/$groupId/members');
    final List<dynamic> data = response.data;
    return data.map((json) => GroupMemberModel.fromJson(json)).toList();
  }

  Future<GroupMemberModel?> getMyGroupMember(String groupId) async {
    final response = await _apiClient.dio.get('/groups/$groupId/members/me');
    if (response.data == null) {
      return null;
    }
    return GroupMemberModel.fromJson(response.data);
  }

  Future<GroupJoinRequestModel> createJoinRequest(String groupId) async {
    final response = await _apiClient.dio.post('/groups/$groupId/join-request');
    return GroupJoinRequestModel.fromJson(response.data);
  }

  Future<GroupJoinRequestModel?> getMyJoinRequest(String groupId) async {
    final response = await _apiClient.dio.get(
      '/groups/$groupId/join-request/me',
    );
    if (response.data == null) {
      return null;
    }
    return GroupJoinRequestModel.fromJson(response.data);
  }

  Future<List<GroupJoinRequestModel>> getJoinRequests(String groupId) async {
    final response = await _apiClient.dio.get('/groups/$groupId/join-requests');
    final List<dynamic> data = response.data;
    return data.map((json) => GroupJoinRequestModel.fromJson(json)).toList();
  }

  Future<GroupJoinRequestModel> approveJoinRequest(
    String requestId,
    String? adminComment,
  ) async {
    final response = await _apiClient.dio.post(
      '/join-requests/$requestId/approve',
      data: {"admin_comment": adminComment ?? "Approved"},
    );
    return GroupJoinRequestModel.fromJson(response.data);
  }

  Future<GroupJoinRequestModel> rejectJoinRequest(
    String requestId,
    String? adminComment,
  ) async {
    final response = await _apiClient.dio.post(
      '/join-requests/$requestId/reject',
      data: {"admin_comment": adminComment ?? "Rejected"},
    );
    return GroupJoinRequestModel.fromJson(response.data);
  }
}
