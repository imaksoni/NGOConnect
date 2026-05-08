class ChannelModel {
  final String id;
  final String groupId;
  final String name;
  final String? slug;
  final String? description;
  final String visibility;
  final String type;
  final String? createdBy;
  final DateTime createdAt;
  final DateTime updatedAt;

  ChannelModel({
    required this.id,
    required this.groupId,
    required this.name,
    this.slug,
    this.description,
    required this.visibility,
    required this.type,
    this.createdBy,
    required this.createdAt,
    required this.updatedAt,
  });

  factory ChannelModel.fromJson(Map<String, dynamic> json) {
    return ChannelModel(
      id: json['id'],
      groupId: json['group_id'],
      name: json['name'],
      slug: json['slug'],
      description: json['description'],
      visibility: json['visibility'] ?? 'public',
      type: json['type'] ?? 'general',
      createdBy: json['created_by'],
      createdAt: DateTime.parse(json['created_at']),
      updatedAt: DateTime.parse(json['updated_at']),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'group_id': groupId,
      'name': name,
      'slug': slug,
      'description': description,
      'visibility': visibility,
      'type': type,
      'created_by': createdBy,
      'created_at': createdAt.toIso8601String(),
      'updated_at': updatedAt.toIso8601String(),
    };
  }
}
