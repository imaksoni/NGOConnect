import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../providers/activity_feed_provider.dart';
import '../../data/models/activity_log_model.dart';
import 'package:intl/intl.dart';

class ActivityFeedScreen extends ConsumerWidget {
  const ActivityFeedScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final activityFeedAsync = ref.watch(globalActivityFeedProvider);

    return Scaffold(
      appBar: AppBar(title: const Text('Activity Feed')),
      body: activityFeedAsync.when(
        data: (feedItems) {
          if (feedItems.isEmpty) {
            return const Center(child: Text('No activity yet.'));
          }
          return ListView.builder(
            itemCount: feedItems.length,
            itemBuilder: (context, index) {
              final item = feedItems[index];
              return _ActivityFeedTile(item: item);
            },
          );
        },
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (error, stack) => Center(child: Text('Error: $error')),
      ),
    );
  }
}

class NgoActivityFeedTab extends ConsumerWidget {
  final String ngoId;

  const NgoActivityFeedTab({super.key, required this.ngoId});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final activityFeedAsync = ref.watch(ngoActivityFeedProvider(ngoId));

    return activityFeedAsync.when(
      data: (feedItems) {
        if (feedItems.isEmpty) {
          return const Center(child: Text('No activity yet.'));
        }
        return ListView.builder(
          itemCount: feedItems.length,
          itemBuilder: (context, index) {
            final item = feedItems[index];
            return _ActivityFeedTile(item: item);
          },
        );
      },
      loading: () => const Center(child: CircularProgressIndicator()),
      error: (error, stack) => Center(child: Text('Error: $error')),
    );
  }
}

class GroupActivityFeedTab extends ConsumerWidget {
  final String groupId;

  const GroupActivityFeedTab({super.key, required this.groupId});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final activityFeedAsync = ref.watch(groupActivityFeedProvider(groupId));

    return activityFeedAsync.when(
      data: (feedItems) {
        if (feedItems.isEmpty) {
          return const Center(child: Text('No activity yet.'));
        }
        return ListView.builder(
          itemCount: feedItems.length,
          itemBuilder: (context, index) {
            final item = feedItems[index];
            return _ActivityFeedTile(item: item);
          },
        );
      },
      loading: () => const Center(child: CircularProgressIndicator()),
      error: (error, stack) => Center(child: Text('Error: $error')),
    );
  }
}

class _ActivityFeedTile extends StatelessWidget {
  final ActivityLogModel item;

  const _ActivityFeedTile({required this.item});

  String _getActionText() {
    switch (item.actionType) {
      case 'event_created':
        return 'created a new event';
      case 'join_request_created':
        return 'requested to join';
      case 'join_request_approved':
        return 'approved a join request';
      case 'join_request_rejected':
        return 'rejected a join request';
      default:
        return 'performed ${item.actionType}';
    }
  }

  @override
  Widget build(BuildContext context) {
    final formattedDate = DateFormat.yMMMd().add_jm().format(item.createdAt);
    return ListTile(
      leading: const Icon(Icons.history),
      title: Text('Someone ${_getActionText()}'),
      subtitle: Text(formattedDate),
    );
  }
}
