import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:intl/intl.dart';

import '../providers/event_provider.dart';

class EventListScreen extends ConsumerWidget {
  final String? ngoId;
  final String? groupId;

  const EventListScreen({super.key, this.ngoId, this.groupId});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final AsyncValue eventsAsyncValue;
    if (ngoId != null) {
      eventsAsyncValue = ref.watch(ngoEventsProvider(ngoId!));
    } else if (groupId != null) {
      eventsAsyncValue = ref.watch(groupEventsProvider(groupId!));
    } else {
      return const Scaffold(body: Center(child: Text('Invalid arguments')));
    }

    return Scaffold(
      appBar: AppBar(title: const Text('Events')),
      body: eventsAsyncValue.when(
        data: (events) {
          if (events.isEmpty) {
            return const Center(child: Text('No events found.'));
          }
          return ListView.builder(
            itemCount: events.length,
            itemBuilder: (context, index) {
              final event = events[index];
              return Card(
                margin: const EdgeInsets.symmetric(
                  horizontal: 16.0,
                  vertical: 8.0,
                ),
                child: ListTile(
                  title: Text(event.title),
                  subtitle: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      if (event.description != null) Text(event.description!),
                      const SizedBox(height: 4),
                      Text(
                        'Start: ${DateFormat.yMd().add_jm().format(event.startTime)}',
                      ),
                      if (event.location != null)
                        Text('Location: ${event.location!}'),
                      const SizedBox(height: 4),
                      Container(
                        padding: const EdgeInsets.symmetric(
                          horizontal: 8,
                          vertical: 2,
                        ),
                        decoration: BoxDecoration(
                          color: event.visibility == 'public'
                              ? Colors.green[100]
                              : Colors.orange[100],
                          borderRadius: BorderRadius.circular(4),
                        ),
                        child: Text(
                          event.visibility == 'public'
                              ? 'Public'
                              : 'Members Only',
                          style: TextStyle(
                            fontSize: 12,
                            color: event.visibility == 'public'
                                ? Colors.green[800]
                                : Colors.orange[800],
                          ),
                        ),
                      ),
                    ],
                  ),
                  isThreeLine: true,
                ),
              );
            },
          );
        },
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (error, _) => Center(child: Text('Error: $error')),
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () {
          if (ngoId != null) {
            context.push('/ngos/$ngoId/events/create');
          } else if (groupId != null) {
            context.push('/groups/$groupId/events/create');
          }
        },
        child: const Icon(Icons.add),
      ),
    );
  }
}
