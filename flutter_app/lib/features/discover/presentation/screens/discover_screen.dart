import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../../core/router/route_constants.dart';
import '../../../ngo/presentation/providers/ngo_provider.dart';

class DiscoverScreen extends ConsumerWidget {
  const DiscoverScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final discoverNgosState = ref.watch(discoverNgosProvider);

    return Scaffold(
      appBar: AppBar(title: const Text('Discover')),
      body: discoverNgosState.when(
        data: (ngos) {
          if (ngos.isEmpty) {
            return const Center(child: Text('No verified NGOs found.'));
          }

          return RefreshIndicator(
            onRefresh: () => ref.refresh(discoverNgosProvider.future),
            child: ListView.builder(
              itemCount: ngos.length,
              itemBuilder: (context, index) {
                final ngo = ngos[index];
                return ListTile(
                  title: Text(ngo.name),
                  subtitle: Text(
                    ngo.about ?? 'No description available',
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                  ),
                  trailing: const Icon(Icons.chevron_right),
                  onTap: () {
                    context.pushNamed(
                      RouteConstants.ngoDetailName,
                      pathParameters: {'slug': ngo.slug},
                    );
                  },
                );
              },
            ),
          );
        },
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (error, stackTrace) => Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Text('Error: $error'),
              const SizedBox(height: 16),
              ElevatedButton(
                onPressed: () {
                  ref.invalidate(discoverNgosProvider);
                },
                child: const Text('Retry'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
