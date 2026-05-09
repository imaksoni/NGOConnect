class ActivityLogModel {
  final String id;
  final String? actorUserId;
  final String actionType;
  final String entityType;
  final String entityId;
  final String? targetUserId;
  final String? ngoId;
  final String? groupId;
  final Map<String, dynamic>? metadataJson;
  final DateTime createdAt;

  ActivityLogModel({
    required this.id,
    this.actorUserId,
    required this.actionType,
    required this.entityType,
    required this.entityId,
    this.targetUserId,
    this.ngoId,
    this.groupId,
    this.metadataJson,
    required this.createdAt,
  });

  factory ActivityLogModel.fromJson(Map<String, dynamic> json) {
    return ActivityLogModel(
      id: json['id'],
      actorUserId: json['actor_user_id'],
      actionType: json['action_type'],
      entityType: json['entity_type'],
      entityId: json['entity_id'],
      targetUserId: json['target_user_id'],
      ngoId: json['ngo_id'],
      groupId: json['group_id'],
      metadataJson: json['metadata_json'],
      createdAt: DateTime.parse(json['created_at']).toLocal(),
    );
  }
}
