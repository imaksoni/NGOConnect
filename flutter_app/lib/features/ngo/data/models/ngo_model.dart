class NgoModel {
  final String id;
  final String name;
  final String slug;
  final String? about;
  final String visibility;
  final String verificationStatus;
  final String? inviteCode;
  final DateTime createdAt;
  final DateTime updatedAt;

  NgoModel({
    required this.id,
    required this.name,
    required this.slug,
    this.about,
    required this.visibility,
    required this.verificationStatus,
    this.inviteCode,
    required this.createdAt,
    required this.updatedAt,
  });

  factory NgoModel.fromJson(Map<String, dynamic> json) {
    return NgoModel(
      id: json['id'],
      name: json['name'],
      slug: json['slug'],
      about: json['about'],
      visibility: json['visibility'] ?? 'private',
      verificationStatus: json['verification_status'] ?? 'pending',
      inviteCode: json['invite_code'],
      createdAt: DateTime.parse(json['created_at']),
      updatedAt: DateTime.parse(json['updated_at']),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'slug': slug,
      'about': about,
      'visibility': visibility,
      'verification_status': verificationStatus,
      'invite_code': inviteCode,
      'created_at': createdAt.toIso8601String(),
      'updated_at': updatedAt.toIso8601String(),
    };
  }
}
