class NotificationModel {
  final String id;
  final String userId;
  final String type;
  final String title;
  final String body;
  final bool isRead;
  final String? entityType;
  final String? entityId;
  final DateTime createdAt;

  NotificationModel({
    required this.id,
    required this.userId,
    required this.type,
    required this.title,
    required this.body,
    required this.isRead,
    this.entityType,
    this.entityId,
    required this.createdAt,
  });

  factory NotificationModel.fromJson(Map<String, dynamic> json) {
    return NotificationModel(
      id: json['id'],
      userId: json['user_id'],
      type: json['type'],
      title: json['title'],
      body: json['body'],
      isRead: json['is_read'],
      entityType: json['entity_type'],
      entityId: json['entity_id'],
      createdAt: DateTime.parse(json['created_at']).toLocal(),
    );
  }
}
