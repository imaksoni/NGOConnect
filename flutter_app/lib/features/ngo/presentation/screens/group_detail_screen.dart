import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../providers/group_provider.dart';
import '../../../groups/presentation/providers/join_request_provider.dart';

class GroupDetailScreen extends ConsumerWidget {
  final String groupId;

  const GroupDetailScreen({super.key, required this.groupId});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final groupState = ref.watch(groupDetailProvider(groupId));

    return Scaffold(
      appBar: AppBar(title: const Text('Group Details')),
      body: groupState.when(
        data: (group) {
          return Padding(
            padding: const EdgeInsets.all(16.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  group.name,
                  style: Theme.of(context).textTheme.headlineMedium,
                ),
                const SizedBox(height: 8),
                Text('Visibility: ${group.visibility}'),
                const SizedBox(height: 16),
                Text('About', style: Theme.of(context).textTheme.titleLarge),
                const SizedBox(height: 8),
                Text(group.about ?? 'No description provided.'),
                const SizedBox(height: 32),
                _buildJoinRequestActions(
                  context,
                  ref,
                  group.id,
                  group.visibility,
                ),
                const SizedBox(height: 16),
                ElevatedButton(
                  onPressed: () {
                    context.push('/groups/${group.id}/channels');
                  },
                  child: const Text('View Channels'),
                ),
              ],
            ),
          );
        },
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (error, _) {
          final errorStr = error.toString().toLowerCase();
          if (errorStr.contains('403') || errorStr.contains('unauthorized')) {
            return const Center(
              child: Padding(
                padding: EdgeInsets.all(16.0),
                child: Text('You are not authorized to view this group.'),
              ),
            );
          }
          return Center(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Text('Error: $error'),
                const SizedBox(height: 16),
                ElevatedButton(
                  onPressed: () {
                    ref.invalidate(groupDetailProvider(groupId));
                  },
                  child: const Text('Retry'),
                ),
              ],
            ),
          );
        },
      ),
    );
  }

  Widget _buildJoinRequestActions(
    BuildContext context,
    WidgetRef ref,
    String groupId,
    String visibility,
  ) {
    final myMemberState = ref.watch(myGroupMemberProvider(groupId));

    return myMemberState.when(
      data: (myMember) {
        final isGroupAdmin =
            myMember?.roleId == 'group_admin'; // Simplification for MVP

        if (isGroupAdmin) {
          return ElevatedButton(
            onPressed: () {
              context.push('/groups/$groupId/join-requests');
            },
            child: const Text('Manage Join Requests'),
          );
        }

        if (myMember != null) {
          return const SizedBox.shrink(); // Already a member, not an admin
        }

        final myRequestState = ref.watch(myJoinRequestProvider(groupId));
        return myRequestState.when(
          data: (myRequest) {
            if (myRequest != null && myRequest.status == 'pending') {
              return const Text(
                'Request Pending',
                style: TextStyle(
                  color: Colors.orange,
                  fontWeight: FontWeight.bold,
                ),
              );
            } else {
              final notifierState = ref.watch(joinRequestNotifierProvider);
              return ElevatedButton(
                onPressed: notifierState.isLoading
                    ? null
                    : () {
                        ref
                            .read(joinRequestNotifierProvider.notifier)
                            .requestToJoin(groupId);
                      },
                child: notifierState.isLoading
                    ? const SizedBox(
                        width: 20,
                        height: 20,
                        child: CircularProgressIndicator(),
                      )
                    : const Text('Request to Join'),
              );
            }
          },
          loading: () => const CircularProgressIndicator(),
          error: (e, st) => const SizedBox.shrink(),
        );
      },
      loading: () => const CircularProgressIndicator(),
      error: (e, st) => const SizedBox.shrink(),
    );
  }
}
