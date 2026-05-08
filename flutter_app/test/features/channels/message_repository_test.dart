import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:dio/dio.dart';
import 'package:ngo_connect/features/channels/data/models/message_model.dart';
import 'package:ngo_connect/features/channels/data/repositories/message_repository.dart';

class MockDio extends Mock implements Dio {}

void main() {
  late MockDio mockDio;
  late MessageRepository repository;

  setUp(() {
    mockDio = MockDio();
    repository = MessageRepository(dio: mockDio);
  });

  group('MessageRepository', () {
    test('getMessages returns a list of MessageModel on success', () async {
      // Arrange
      final responsePayload = [
        {
          'id': 'msg-1',
          'channel_id': 'ch-1',
          'sender_id': 'user-1',
          'content': 'Hello',
          'type': 'text',
          'created_at': '2023-01-01T12:00:00Z',
          'updated_at': '2023-01-01T12:00:00Z',
          'attachments': [],
        },
      ];

      when(
        () => mockDio.get(
          '/channels/ch-1/messages',
          queryParameters: any(named: 'queryParameters'),
        ),
      ).thenAnswer(
        (_) async => Response(
          requestOptions: RequestOptions(path: ''),
          data: responsePayload,
          statusCode: 200,
        ),
      );

      // Act
      final messages = await repository.getMessages('ch-1');

      // Assert
      expect(messages, isA<List<MessageModel>>());
      expect(messages.length, 1);
      expect(messages.first.content, 'Hello');
    });

    test('createMessage returns a MessageModel on success', () async {
      // Arrange
      final responsePayload = {
        'id': 'msg-2',
        'channel_id': 'ch-1',
        'sender_id': 'user-1',
        'content': 'New Message',
        'type': 'text',
        'created_at': '2023-01-01T12:05:00Z',
        'updated_at': '2023-01-01T12:05:00Z',
        'attachments': [],
      };

      when(
        () => mockDio.post('/channels/ch-1/messages', data: any(named: 'data')),
      ).thenAnswer(
        (_) async => Response(
          requestOptions: RequestOptions(path: ''),
          data: responsePayload,
          statusCode: 201,
        ),
      );

      // Act
      final message = await repository.createMessage('ch-1', 'New Message');

      // Assert
      expect(message, isA<MessageModel>());
      expect(message.content, 'New Message');
    });
  });
}
