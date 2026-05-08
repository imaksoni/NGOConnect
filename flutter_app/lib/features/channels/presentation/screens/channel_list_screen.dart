import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../providers/channel_provider.dart';

class ChannelListScreen extends ConsumerWidget {
  final String groupId;

  const ChannelListScreen({super.key, required this.groupId});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final channelsState = ref.watch(groupChannelsProvider(groupId));

    return Scaffold(
      appBar: AppBar(title: const Text('Channels')),
      body: channelsState.when(
        data: (channels) {
          if (channels.isEmpty) {
            return const Center(child: Text('No channels found.'));
          }
          return ListView.builder(
            itemCount: channels.length,
            itemBuilder: (context, index) {
              final channel = channels[index];
              return ListTile(
                title: Text(channel.name),
                subtitle: Text(
                  'Type: ${channel.type} | Visibility: ${channel.visibility}',
                ),
                onTap: () {
                  context.push('/channels/${channel.id}');
                },
              );
            },
          );
        },
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (error, _) => Center(child: Text('Error: $error')),
      ),
    );
  }
}
