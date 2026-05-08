import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../data/models/message_model.dart';
import '../../data/repositories/message_repository.dart';

final messageRepositoryProvider = Provider<MessageRepository>((ref) {
  return MessageRepository();
});

final messagesProvider = FutureProvider.family<List<MessageModel>, String>((
  ref,
  channelId,
) async {
  final repository = ref.watch(messageRepositoryProvider);
  return repository.getMessages(channelId);
});
