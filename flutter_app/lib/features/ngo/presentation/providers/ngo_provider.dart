import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../../features/auth/presentation/providers/auth_provider.dart';
import '../../data/repositories/ngo_repository.dart';
import '../../data/models/ngo_model.dart';

final ngoRepositoryProvider = Provider<NgoRepository>((ref) {
  final apiClient = ref.watch(apiClientProvider);
  return NgoRepository(apiClient: apiClient);
});

final discoverNgosProvider = FutureProvider.autoDispose<List<NgoModel>>((
  ref,
) async {
  final repository = ref.watch(ngoRepositoryProvider);
  return repository.getDiscoverableNgos();
});

final searchNgosProvider = FutureProvider.family.autoDispose<List<NgoModel>, String>((
  ref,
  query,
) async {
  final repository = ref.watch(ngoRepositoryProvider);
  if (query.isEmpty) {
    return repository.getDiscoverableNgos();
  }
  return repository.searchNgos(query);
});

final ngoDetailProvider = FutureProvider.family.autoDispose<NgoModel, String>((
  ref,
  slug,
) async {
  final repository = ref.watch(ngoRepositoryProvider);
  return repository.getNgoBySlug(slug);
});
