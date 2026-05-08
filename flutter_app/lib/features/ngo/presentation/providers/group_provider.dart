import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../../features/auth/presentation/providers/auth_provider.dart';
import '../../data/models/group_model.dart';

final groupListProvider = FutureProvider.family<List<GroupModel>, String>((
  ref,
  ngoId,
) async {
  final apiClient = ref.watch(apiClientProvider);
  final response = await apiClient.dio.get('/ngos/$ngoId/groups');

  if (response.statusCode == 200) {
    final List<dynamic> data = response.data;
    return data.map((json) => GroupModel.fromJson(json)).toList();
  } else {
    throw Exception('Failed to load groups');
  }
});

final groupDetailProvider = FutureProvider.family<GroupModel, String>((
  ref,
  groupId,
) async {
  final apiClient = ref.watch(apiClientProvider);
  final response = await apiClient.dio.get('/groups/$groupId');

  if (response.statusCode == 200) {
    return GroupModel.fromJson(response.data);
  } else {
    throw Exception('Failed to load group details');
  }
});
