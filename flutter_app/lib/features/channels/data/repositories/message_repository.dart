import 'package:dio/dio.dart';
import '../../../../core/network/api_client.dart';
import '../models/message_model.dart';

class MessageRepository {
  final Dio _dio;

  MessageRepository({Dio? dio}) : _dio = dio ?? ApiClient().dio;

  Future<List<MessageModel>> getMessages(
    String channelId, {
    int limit = 50,
    int offset = 0,
  }) async {
    try {
      final response = await _dio.get(
        '/channels/$channelId/messages',
        queryParameters: {'limit': limit, 'offset': offset},
      );
      final List data = response.data;
      return data.map((json) => MessageModel.fromJson(json)).toList();
    } catch (e) {
      rethrow;
    }
  }

  Future<MessageModel> createMessage(
    String channelId,
    String content, {
    String type = 'text',
  }) async {
    try {
      final response = await _dio.post(
        '/channels/$channelId/messages',
        data: {'content': content, 'type': type},
      );
      return MessageModel.fromJson(response.data);
    } catch (e) {
      rethrow;
    }
  }

  Future<MessageAttachmentModel> createAttachmentMetadata(
    String messageId,
    Map<String, dynamic> attachmentData,
  ) async {
    try {
      final response = await _dio.post(
        '/messages/$messageId/attachments',
        data: attachmentData,
      );
      return MessageAttachmentModel.fromJson(response.data);
    } catch (e) {
      rethrow;
    }
  }
}
