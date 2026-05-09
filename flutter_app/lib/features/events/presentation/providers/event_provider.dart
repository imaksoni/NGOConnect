import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../data/models/event_model.dart';
import '../../data/repositories/event_repository.dart';

final eventRepositoryProvider = Provider<EventRepository>((ref) {
  return EventRepository();
});

final ngoEventsProvider = FutureProvider.family<List<EventModel>, String>((
  ref,
  ngoId,
) {
  final repository = ref.watch(eventRepositoryProvider);
  return repository.getNgoEvents(ngoId);
});

final groupEventsProvider = FutureProvider.family<List<EventModel>, String>((
  ref,
  groupId,
) {
  final repository = ref.watch(eventRepositoryProvider);
  return repository.getGroupEvents(groupId);
});

class EventCreationNotifier extends Notifier<AsyncValue<void>> {
  @override
  AsyncValue<void> build() {
    return const AsyncValue.data(null);
  }

  Future<bool> createNgoEvent(
    String ngoId,
    Map<String, dynamic> eventData,
  ) async {
    state = const AsyncValue.loading();
    try {
      await ref.read(eventRepositoryProvider).createNgoEvent(ngoId, eventData);
      state = const AsyncValue.data(null);
      ref.invalidate(ngoEventsProvider(ngoId));
      return true;
    } catch (e, st) {
      state = AsyncValue.error(e, st);
      return false;
    }
  }

  Future<bool> createGroupEvent(
    String groupId,
    Map<String, dynamic> eventData,
  ) async {
    state = const AsyncValue.loading();
    try {
      await ref
          .read(eventRepositoryProvider)
          .createGroupEvent(groupId, eventData);
      state = const AsyncValue.data(null);
      ref.invalidate(groupEventsProvider(groupId));
      return true;
    } catch (e, st) {
      state = AsyncValue.error(e, st);
      return false;
    }
  }
}

final eventCreationProvider =
    NotifierProvider<EventCreationNotifier, AsyncValue<void>>(() {
      return EventCreationNotifier();
    });
