import 'dart:async';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../data/models/message_model.dart';
import '../../data/repositories/message_repository.dart';
import '../../data/repositories/channel_websocket_repository.dart';

final messageRepositoryProvider = Provider<MessageRepository>((ref) {
  return MessageRepository();
});

final channelWebSocketRepositoryProvider = Provider.autoDispose
    .family<ChannelWebSocketRepository, String>((ref, channelId) {
      final repo = ChannelWebSocketRepository();
      ref.onDispose(() {
        repo.disconnect();
      });
      return repo;
    });

class MessagesNotifier
    extends AutoDisposeFamilyAsyncNotifier<List<MessageModel>, String> {
  StreamSubscription<MessageModel>? _wsSubscription;

  @override
  FutureOr<List<MessageModel>> build(String arg) async {
    final repository = ref.watch(messageRepositoryProvider);
    final wsRepository = ref.watch(channelWebSocketRepositoryProvider(arg));

    ref.onDispose(() {
      _wsSubscription?.cancel();
    });

    // 1. Fetch initial messages via REST
    final initialMessages = await repository.getMessages(arg);

    // 2. Connect and listen to WebSocket
    await wsRepository.connect(arg);
    _wsSubscription = wsRepository.messages.listen((newMessage) {
      final currentState = state.valueOrNull ?? [];
      if (!currentState.any((m) => m.id == newMessage.id)) {
        state = AsyncData([newMessage, ...currentState]);
      }
    });

    return initialMessages;
  }
}

final messagesProvider = AsyncNotifierProvider.autoDispose
    .family<MessagesNotifier, List<MessageModel>, String>(MessagesNotifier.new);
