import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../providers/channel_provider.dart';

class ChannelDetailScreen extends ConsumerWidget {
  final String channelId;

  const ChannelDetailScreen({super.key, required this.channelId});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final channelState = ref.watch(channelDetailProvider(channelId));

    return Scaffold(
      appBar: AppBar(title: const Text('Channel Details')),
      body: channelState.when(
        data: (channel) {
          return Padding(
            padding: const EdgeInsets.all(16.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  channel.name,
                  style: Theme.of(context).textTheme.headlineMedium,
                ),
                const SizedBox(height: 8),
                Text('Type: ${channel.type}'),
                Text('Visibility: ${channel.visibility}'),
                const SizedBox(height: 16),
                Text(
                  'Description',
                  style: Theme.of(context).textTheme.titleLarge,
                ),
                const SizedBox(height: 8),
                Text(channel.description ?? 'No description provided.'),
                const SizedBox(height: 32),
                const Center(
                  child: Text(
                    'Chat UI coming soon...',
                    style: TextStyle(color: Colors.grey),
                  ),
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
