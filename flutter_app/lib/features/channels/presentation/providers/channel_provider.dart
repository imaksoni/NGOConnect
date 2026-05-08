import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../data/models/channel_model.dart';
import '../../data/repositories/channel_repository.dart';
import '../../../auth/presentation/providers/auth_provider.dart';

final channelRepositoryProvider = Provider<ChannelRepository>((ref) {
  final apiClient = ref.watch(apiClientProvider);
  return ChannelRepository(apiClient: apiClient);
});

final groupChannelsProvider = FutureProvider.family<List<ChannelModel>, String>(
  (ref, groupId) async {
    final repository = ref.watch(channelRepositoryProvider);
    return repository.getChannelsByGroup(groupId);
  },
);

final channelDetailProvider = FutureProvider.family<ChannelModel, String>((
  ref,
  channelId,
) async {
  final repository = ref.watch(channelRepositoryProvider);
  return repository.getChannel(channelId);
});
