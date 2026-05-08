import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../../features/auth/presentation/providers/auth_provider.dart';
import '../../../ngo/data/models/group_model.dart';
import '../../data/repositories/group_repository.dart';

final groupRepositoryProvider = Provider<GroupRepository>((ref) {
  final apiClient = ref.watch(apiClientProvider);
  return GroupRepository(apiClient: apiClient);
});

final groupMembersProvider =
    FutureProvider.family<List<GroupMemberModel>, String>((ref, groupId) {
      final repository = ref.watch(groupRepositoryProvider);
      return repository.getGroupMembers(groupId);
    });

final joinRequestsProvider =
    FutureProvider.family<List<GroupJoinRequestModel>, String>((ref, groupId) {
      final repository = ref.watch(groupRepositoryProvider);
      return repository.getJoinRequests(groupId);
    });

final myJoinRequestProvider =
    FutureProvider.family<GroupJoinRequestModel?, String>((ref, groupId) {
      final repository = ref.watch(groupRepositoryProvider);
      return repository.getMyJoinRequest(groupId);
    });

final myGroupMemberProvider = FutureProvider.family<GroupMemberModel?, String>((
  ref,
  groupId,
) {
  final repository = ref.watch(groupRepositoryProvider);
  return repository.getMyGroupMember(groupId);
});

class JoinRequestNotifier extends Notifier<AsyncValue<void>> {
  @override
  AsyncValue<void> build() {
    return const AsyncValue.data(null);
  }

  Future<void> requestToJoin(String groupId) async {
    state = const AsyncValue.loading();
    try {
      final repository = ref.read(groupRepositoryProvider);
      await repository.createJoinRequest(groupId);
      state = const AsyncValue.data(null);
      ref.invalidate(joinRequestsProvider(groupId));
      ref.invalidate(myJoinRequestProvider(groupId));
    } catch (e, st) {
      state = AsyncValue.error(e, st);
    }
  }

  Future<void> approveRequest(
    String requestId,
    String groupId, {
    String? adminComment,
  }) async {
    state = const AsyncValue.loading();
    try {
      final repository = ref.read(groupRepositoryProvider);
      await repository.approveJoinRequest(requestId, adminComment);
      state = const AsyncValue.data(null);
      ref.invalidate(joinRequestsProvider(groupId));
      ref.invalidate(groupMembersProvider(groupId));
    } catch (e, st) {
      state = AsyncValue.error(e, st);
    }
  }

  Future<void> rejectRequest(
    String requestId,
    String groupId, {
    String? adminComment,
  }) async {
    state = const AsyncValue.loading();
    try {
      final repository = ref.read(groupRepositoryProvider);
      await repository.rejectJoinRequest(requestId, adminComment);
      state = const AsyncValue.data(null);
      ref.invalidate(joinRequestsProvider(groupId));
    } catch (e, st) {
      state = AsyncValue.error(e, st);
    }
  }
}

final joinRequestNotifierProvider =
    NotifierProvider<JoinRequestNotifier, AsyncValue<void>>(() {
      return JoinRequestNotifier();
    });
