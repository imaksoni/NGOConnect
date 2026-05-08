class GroupModel {
  final String id;
  final String ngoId;
  final String name;
  final String slug;
  final String? about;
  final String visibility;
  final String? createdBy;
  final DateTime createdAt;
  final DateTime updatedAt;

  GroupModel({
    required this.id,
    required this.ngoId,
    required this.name,
    required this.slug,
    this.about,
    required this.visibility,
    this.createdBy,
    required this.createdAt,
    required this.updatedAt,
  });

  factory GroupModel.fromJson(Map<String, dynamic> json) {
    return GroupModel(
      id: json['id'],
      ngoId: json['ngo_id'],
      name: json['name'],
      slug: json['slug'],
      about: json['about'],
      visibility: json['visibility'] ?? 'invite_only',
      createdBy: json['created_by'],
      createdAt: DateTime.parse(json['created_at']),
      updatedAt: DateTime.parse(json['updated_at']),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'ngo_id': ngoId,
      'name': name,
      'slug': slug,
      'about': about,
      'visibility': visibility,
      'created_by': createdBy,
      'created_at': createdAt.toIso8601String(),
      'updated_at': updatedAt.toIso8601String(),
    };
  }
}

class GroupJoinRequestModel {
  final String id;
  final String groupId;
  final String userId;
  final String status;
  final DateTime requestedAt;
  final String? adminComment;
  final Map<String, dynamic>? user;

  GroupJoinRequestModel({
    required this.id,
    required this.groupId,
    required this.userId,
    required this.status,
    required this.requestedAt,
    this.adminComment,
    this.user,
  });

  factory GroupJoinRequestModel.fromJson(Map<String, dynamic> json) {
    return GroupJoinRequestModel(
      id: json['id'],
      groupId: json['group_id'],
      userId: json['user_id'],
      status: json['status'],
      requestedAt: DateTime.parse(json['requested_at']),
      adminComment: json['admin_comment'],
      user: json['user'],
    );
  }
}

class GroupMemberModel {
  final String userId;
  final String groupId;
  final String roleId;
  final String status;
  final Map<String, dynamic>? role;

  GroupMemberModel({
    required this.userId,
    required this.groupId,
    required this.roleId,
    required this.status,
    this.role,
  });

  factory GroupMemberModel.fromJson(Map<String, dynamic> json) {
    return GroupMemberModel(
      userId: json['user_id'],
      groupId: json['group_id'],
      roleId: json['role_id'],
      status: json['status'],
      role: json['role'],
    );
  }
}
