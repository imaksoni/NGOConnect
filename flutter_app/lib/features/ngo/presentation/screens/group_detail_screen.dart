import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../providers/group_provider.dart';

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
        error: (error, _) => Center(child: Text('Error: $error')),
      ),
    );
  }
}
