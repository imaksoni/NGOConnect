class EventModel {
  final String id;
  final String? ngoId;
  final String? groupId;
  final String title;
  final String? description;
  final DateTime startTime;
  final DateTime endTime;
  final String? location;
  final String visibility;

  EventModel({
    required this.id,
    this.ngoId,
    this.groupId,
    required this.title,
    this.description,
    required this.startTime,
    required this.endTime,
    this.location,
    required this.visibility,
  });

  factory EventModel.fromJson(Map<String, dynamic> json) {
    return EventModel(
      id: json['id'],
      ngoId: json['ngo_id'],
      groupId: json['group_id'],
      title: json['title'],
      description: json['description'],
      startTime: DateTime.parse(json['start_time']),
      endTime: DateTime.parse(json['end_time']),
      location: json['location'],
      visibility: json['visibility'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'ngo_id': ngoId,
      'group_id': groupId,
      'title': title,
      'description': description,
      'start_time': startTime.toIso8601String(),
      'end_time': endTime.toIso8601String(),
      'location': location,
      'visibility': visibility,
    };
  }
}
