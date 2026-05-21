import 'dart:convert';
import 'package:web_socket_channel/web_socket_channel.dart';
import '../../../auth/data/repositories/token_repository.dart';
import '../models/message_model.dart';
import '../../../../core/logger/app_logger.dart';

import 'dart:async';

class ChannelWebSocketRepository {
  WebSocketChannel? _channel;
  final String _baseUrl;
  final TokenRepository _tokenRepository;

  final _messageController = StreamController<MessageModel>.broadcast();
  Timer? _reconnectTimer;
  bool _isIntentionalDisconnect = false;

  ChannelWebSocketRepository({
    String? baseUrl,
    TokenRepository? tokenRepository,
  }) : _baseUrl = baseUrl ?? 'ws://10.0.2.2:8000',
       _tokenRepository = tokenRepository ?? TokenRepository();

  Stream<MessageModel> get messages => _messageController.stream;

  Future<void> connect(String channelId) async {
    if (_channel != null) return; // Already connected or connecting

    _isIntentionalDisconnect = false;
    final token = await _tokenRepository.getAccessToken();
    if (token == null) return;

    try {
      final wsUrl = Uri.parse('$_baseUrl/ws/channels/$channelId?token=$token');
      _channel = WebSocketChannel.connect(wsUrl);
      AppLogger.info('WebSocket connected to channel: $channelId');

      _channel!.stream.listen(
        (event) {
          final data = jsonDecode(event);
          _messageController.add(MessageModel.fromJson(data));
        },
        onDone: () {
          AppLogger.info('WebSocket closed for channel: $channelId');
          _channel = null;
          if (!_isIntentionalDisconnect) {
            _scheduleReconnect(channelId);
          }
        },
        onError: (error) {
          AppLogger.error('WebSocket error on channel $channelId', error: error);
          _channel = null;
          if (!_isIntentionalDisconnect) {
            _scheduleReconnect(channelId);
          }
        },
      );
    } catch (e, st) {
      AppLogger.error('WebSocket connection failed for channel $channelId', error: e, stackTrace: st);
      _channel = null;
      if (!_isIntentionalDisconnect) {
        _scheduleReconnect(channelId);
      }
    }
  }

  void _scheduleReconnect(String channelId) {
    _reconnectTimer?.cancel();
    _reconnectTimer = Timer(const Duration(seconds: 3), () {
      connect(channelId);
    });
  }

  void disconnect() {
    _isIntentionalDisconnect = true;
    _reconnectTimer?.cancel();
    _channel?.sink.close();
    _channel = null;
  }

  void dispose() {
    disconnect();
    _messageController.close();
  }
}
