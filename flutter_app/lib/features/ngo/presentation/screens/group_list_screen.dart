import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../../core/router/route_constants.dart';
import '../providers/group_provider.dart';

class GroupListScreen extends ConsumerWidget {
  final String ngoId;

  const GroupListScreen({super.key, required this.ngoId});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final groupsState = ref.watch(groupListProvider(ngoId));

    return Scaffold(
      appBar: AppBar(title: const Text('Groups')),
      body: groupsState.when(
        data: (groups) {
          if (groups.isEmpty) {
            return const Center(child: Text('No groups found.'));
          }
          return ListView.builder(
            itemCount: groups.length,
            itemBuilder: (context, index) {
              final group = groups[index];
              return ListTile(
                title: Text(group.name),
                subtitle: Text(group.visibility),
                onTap: () {
                  context.pushNamed(
                    RouteConstants.groupDetailName,
                    pathParameters: {'groupId': group.id},
                  );
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
