import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:mocktail/mocktail.dart';
import 'package:ngo_connect/features/events/data/models/event_model.dart';
import 'package:ngo_connect/features/events/data/repositories/event_repository.dart';
import 'package:ngo_connect/features/events/presentation/providers/event_provider.dart';

class MockEventRepository extends Mock implements EventRepository {}

void main() {
  late MockEventRepository mockRepository;
  late ProviderContainer container;

  setUp(() {
    mockRepository = MockEventRepository();
    container = ProviderContainer(
      overrides: [eventRepositoryProvider.overrideWithValue(mockRepository)],
    );
  });

  tearDown(() {
    container.dispose();
  });

  group('EventProvider Tests', () {
    test('ngoEventsProvider fetches and returns events', () async {
      final mockEvents = [
        EventModel(
          id: '1',
          title: 'Test Event',
          startTime: DateTime.now(),
          endTime: DateTime.now().add(const Duration(hours: 1)),
          visibility: 'public',
        ),
      ];

      when(
        () => mockRepository.getNgoEvents('ngo1'),
      ).thenAnswer((_) async => mockEvents);

      final eventsAsync = container.read(ngoEventsProvider('ngo1'));
      expect(eventsAsync, const AsyncValue<List<EventModel>>.loading());

      final result = await container.read(ngoEventsProvider('ngo1').future);
      expect(result, mockEvents);
      verify(() => mockRepository.getNgoEvents('ngo1')).called(1);
    });

    test('createNgoEvent updates state correctly', () async {
      when(() => mockRepository.createNgoEvent('ngo1', any())).thenAnswer(
        (_) async => EventModel(
          id: '1',
          title: 'New',
          startTime: DateTime.now(),
          endTime: DateTime.now(),
          visibility: 'public',
        ),
      );

      final notifier = container.read(eventCreationProvider.notifier);
      final result = await notifier.createNgoEvent('ngo1', {'title': 'New'});

      expect(result, isTrue);
      expect(container.read(eventCreationProvider).hasValue, isTrue);
      verify(() => mockRepository.createNgoEvent('ngo1', any())).called(1);
    });
  });
}
