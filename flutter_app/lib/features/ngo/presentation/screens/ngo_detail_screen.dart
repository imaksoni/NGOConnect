import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../providers/ngo_provider.dart';
import '../../data/models/ngo_model.dart';

class NgoDetailScreen extends ConsumerWidget {
  final String slug;

  const NgoDetailScreen({super.key, required this.slug});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final ngoState = ref.watch(ngoDetailProvider(slug));

    return Scaffold(
      appBar: AppBar(title: Text(ngoState.value?.name ?? 'Loading...')),
      body: ngoState.when(
        data: (ngo) => _NgoDetailContent(ngo: ngo),
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (error, stackTrace) => Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Text('Error: $error'),
              const SizedBox(height: 16),
              ElevatedButton(
                onPressed: () {
                  ref.invalidate(ngoDetailProvider(slug));
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

class _NgoDetailContent extends StatelessWidget {
  final NgoModel ngo;

  const _NgoDetailContent({required this.ngo});

  @override
  Widget build(BuildContext context) {
    return DefaultTabController(
      length: 1,
      child: Column(
        children: [
          Padding(
            padding: const EdgeInsets.all(16.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  ngo.name,
                  style: Theme.of(context).textTheme.headlineMedium,
                ),
                const SizedBox(height: 8),
                Row(
                  children: [
                    _buildBadge(
                      context,
                      ngo.visibility == 'public' ? 'Public' : 'Private',
                      ngo.visibility == 'public' ? Colors.blue : Colors.grey,
                    ),
                    const SizedBox(width: 8),
                    _buildBadge(
                      context,
                      ngo.verificationStatus == 'verified'
                          ? 'Verified'
                          : ngo.verificationStatus == 'pending'
                          ? 'Pending'
                          : 'Unverified',
                      ngo.verificationStatus == 'verified'
                          ? Colors.green
                          : ngo.verificationStatus == 'pending'
                          ? Colors.orange
                          : Colors.red,
                    ),
                  ],
                ),
              ],
            ),
          ),
          const TabBar(tabs: [Tab(text: 'About')]),
          Expanded(child: TabBarView(children: [_buildAboutTab(context)])),
        ],
      ),
    );
  }

  Widget _buildBadge(BuildContext context, String text, Color color) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.1),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: color),
      ),
      child: Text(
        text,
        style: TextStyle(
          color: color,
          fontSize: 12,
          fontWeight: FontWeight.bold,
        ),
      ),
    );
  }

  Widget _buildAboutTab(BuildContext context) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'About ${ngo.name}',
            style: Theme.of(context).textTheme.titleLarge,
          ),
          const SizedBox(height: 16),
          Text(
            ngo.about ?? 'No description provided.',
            style: Theme.of(context).textTheme.bodyLarge,
          ),
        ],
      ),
    );
  }
}
