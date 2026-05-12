class UserModel {
  final String id;
  final String email;
  final String? firstName;
  final String? lastName;
  final bool isActive;
  final bool isPlatformAdmin;

  UserModel({
    required this.id,
    required this.email,
    this.firstName,
    this.lastName,
    required this.isActive,
    this.isPlatformAdmin = false,
  });

  factory UserModel.fromJson(Map<String, dynamic> json) {
    return UserModel(
      id: json['id'],
      email: json['email'],
      firstName: json['first_name'],
      lastName: json['last_name'],
      isActive: json['is_active'] ?? true,
      isPlatformAdmin: json['is_platform_admin'] ?? false,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'email': email,
      'first_name': firstName,
      'last_name': lastName,
      'is_active': isActive,
      'is_platform_admin': isPlatformAdmin,
    };
  }
}
