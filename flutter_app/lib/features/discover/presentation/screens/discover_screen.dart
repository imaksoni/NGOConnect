import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../../core/router/route_constants.dart';
import '../../../ngo/presentation/providers/ngo_provider.dart';

class DiscoverScreen extends ConsumerStatefulWidget {
  const DiscoverScreen({super.key});

  @override
  ConsumerState<DiscoverScreen> createState() => _DiscoverScreenState();
}

class _DiscoverScreenState extends ConsumerState<DiscoverScreen> {
  final _searchController = TextEditingController();
  String _searchQuery = '';

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final discoverNgosState = _searchQuery.isEmpty
        ? ref.watch(discoverNgosProvider)
        : ref.watch(searchNgosProvider(_searchQuery));

    return Scaffold(
      appBar: AppBar(
        title: const Text('Discover'),
        bottom: PreferredSize(
          preferredSize: const Size.fromHeight(60.0),
          child: Padding(
            padding: const EdgeInsets.all(8.0),
            child: TextField(
              controller: _searchController,
              decoration: InputDecoration(
                hintText: 'Search NGOs...',
                prefixIcon: const Icon(Icons.search),
                suffixIcon: _searchQuery.isNotEmpty
                    ? IconButton(
                        icon: const Icon(Icons.clear),
                        onPressed: () {
                          _searchController.clear();
                          setState(() {
                            _searchQuery = '';
                          });
                        },
                      )
                    : null,
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(8.0),
                ),
                filled: true,
                fillColor: Theme.of(context).cardColor,
              ),
              onSubmitted: (value) {
                setState(() {
                  _searchQuery = value.trim();
                });
              },
            ),
          ),
        ),
      ),
      body: discoverNgosState.when(
        data: (ngos) {
          if (ngos.isEmpty) {
            return const Center(child: Text('No verified NGOs found.'));
          }

          return RefreshIndicator(
            onRefresh: () async {
              if (_searchQuery.isEmpty) {
                ref.invalidate(discoverNgosProvider);
              } else {
                ref.invalidate(searchNgosProvider(_searchQuery));
              }
            },
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
                  if (_searchQuery.isEmpty) {
                    ref.invalidate(discoverNgosProvider);
                  } else {
                    ref.invalidate(searchNgosProvider(_searchQuery));
                  }
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
