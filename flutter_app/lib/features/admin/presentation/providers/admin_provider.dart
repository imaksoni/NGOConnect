import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../data/repositories/admin_repository.dart';
import '../../../ngo/data/models/ngo_model.dart';

final adminRepositoryProvider = Provider((ref) => AdminRepository());

final verificationRequestsProvider = FutureProvider.autoDispose<List<NgoModel>>(
  (ref) async {
    final repository = ref.watch(adminRepositoryProvider);
    return repository.getVerificationRequests();
  },
);

final auditLogsProvider =
    FutureProvider.autoDispose<List<Map<String, dynamic>>>((ref) async {
      final repository = ref.watch(adminRepositoryProvider);
      return repository.getAuditLogs();
    });
