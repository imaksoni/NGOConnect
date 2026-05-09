import 'package:dio/dio.dart';
import '../../../../core/network/api_client.dart';
import '../models/event_model.dart';

class EventRepository {
  final Dio _dio = ApiClient().dio;

  Future<List<EventModel>> getNgoEvents(String ngoId) async {
    final response = await _dio.get('/ngos/$ngoId/events');
    return (response.data as List).map((e) => EventModel.fromJson(e)).toList();
  }

  Future<List<EventModel>> getGroupEvents(String groupId) async {
    final response = await _dio.get('/groups/$groupId/events');
    return (response.data as List).map((e) => EventModel.fromJson(e)).toList();
  }

  Future<EventModel> createNgoEvent(
    String ngoId,
    Map<String, dynamic> eventData,
  ) async {
    final response = await _dio.post('/ngos/$ngoId/events', data: eventData);
    return EventModel.fromJson(response.data);
  }

  Future<EventModel> createGroupEvent(
    String groupId,
    Map<String, dynamic> eventData,
  ) async {
    final response = await _dio.post(
      '/groups/$groupId/events',
      data: eventData,
    );
    return EventModel.fromJson(response.data);
  }
}
