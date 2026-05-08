import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../providers/join_request_provider.dart';

class JoinRequestsScreen extends ConsumerWidget {
  final String groupId;

  const JoinRequestsScreen({super.key, required this.groupId});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final requestsState = ref.watch(joinRequestsProvider(groupId));
    final notifierState = ref.watch(joinRequestNotifierProvider);

    return Scaffold(
      appBar: AppBar(title: const Text('Manage Join Requests')),
      body: requestsState.when(
        data: (requests) {
          final pendingRequests = requests
              .where((r) => r.status == 'pending')
              .toList();

          if (pendingRequests.isEmpty) {
            return const Center(child: Text('No pending requests.'));
          }

          return ListView.builder(
            itemCount: pendingRequests.length,
            itemBuilder: (context, index) {
              final request = pendingRequests[index];
              return ListTile(
                title: Text('User ID: ${request.userId}'),
                subtitle: Text('Requested at: ${request.requestedAt}'),
                trailing: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    IconButton(
                      icon: const Icon(Icons.check, color: Colors.green),
                      onPressed: notifierState.isLoading
                          ? null
                          : () => _showReviewDialog(
                              context,
                              ref,
                              request.id,
                              true,
                            ),
                    ),
                    IconButton(
                      icon: const Icon(Icons.close, color: Colors.red),
                      onPressed: notifierState.isLoading
                          ? null
                          : () => _showReviewDialog(
                              context,
                              ref,
                              request.id,
                              false,
                            ),
                    ),
                  ],
                ),
              );
            },
          );
        },
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (e, st) => Center(child: Text('Error: $e')),
      ),
    );
  }

  Future<void> _showReviewDialog(
    BuildContext context,
    WidgetRef ref,
    String requestId,
    bool isApprove,
  ) async {
    final commentController = TextEditingController();
    return showDialog(
      context: context,
      builder: (context) {
        return AlertDialog(
          title: Text(isApprove ? 'Approve Request' : 'Reject Request'),
          content: TextField(
            controller: commentController,
            decoration: const InputDecoration(hintText: "Optional comment"),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.of(context).pop(),
              child: const Text('Cancel'),
            ),
            TextButton(
              onPressed: () {
                final comment = commentController.text.isNotEmpty
                    ? commentController.text
                    : null;
                if (isApprove) {
                  ref
                      .read(joinRequestNotifierProvider.notifier)
                      .approveRequest(
                        requestId,
                        groupId,
                        adminComment: comment,
                      );
                } else {
                  ref
                      .read(joinRequestNotifierProvider.notifier)
                      .rejectRequest(requestId, groupId, adminComment: comment);
                }
                Navigator.of(context).pop();
              },
              child: const Text('Confirm'),
            ),
          ],
        );
      },
    );
  }
}
