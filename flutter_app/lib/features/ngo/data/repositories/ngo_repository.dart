import '../../../../core/network/api_client.dart';
import '../models/ngo_model.dart';

class NgoRepository {
  final ApiClient _apiClient;

  NgoRepository({required ApiClient apiClient}) : _apiClient = apiClient;

  Future<List<NgoModel>> getDiscoverableNgos() async {
    final response = await _apiClient.dio.get('/ngos/discover');
    final List<dynamic> data = response.data;
    return data.map((json) => NgoModel.fromJson(json)).toList();
  }

  Future<NgoModel> getNgoBySlug(String slug) async {
    final response = await _apiClient.dio.get('/ngos/slug/$slug');
    return NgoModel.fromJson(response.data);
  }
}
