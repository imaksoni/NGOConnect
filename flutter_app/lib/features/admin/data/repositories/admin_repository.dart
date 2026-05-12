import 'package:dio/dio.dart';
import '../../../../core/network/api_client.dart';
import '../../../ngo/data/models/ngo_model.dart';

class AdminRepository {
  final Dio _dio = ApiClient().dio;

  Future<List<NgoModel>> getVerificationRequests() async {
    try {
      final response = await _dio.get(
        '/admin/moderation/verification-requests',
      );
      return (response.data as List)
          .map((json) => NgoModel.fromJson(json))
          .toList();
    } catch (e) {
      throw Exception('Failed to load verification requests: $e');
    }
  }

  Future<List<Map<String, dynamic>>> getAuditLogs() async {
    try {
      final response = await _dio.get('/admin/audit-logs');
      return List<Map<String, dynamic>>.from(response.data);
    } catch (e) {
      throw Exception('Failed to load audit logs: $e');
    }
  }

  Future<void> verifyNgo(String ngoId) async {
    try {
      await _dio.post('/admin/ngos/$ngoId/verify');
    } catch (e) {
      throw Exception('Failed to verify NGO: $e');
    }
  }

  Future<void> rejectNgoVerification(String ngoId) async {
    try {
      await _dio.post('/admin/ngos/$ngoId/reject-verification');
    } catch (e) {
      throw Exception('Failed to reject NGO verification: $e');
    }
  }
}
