class TokenModel {
  final String accessToken;
  final String refreshToken;
  final String tokenType;

  TokenModel({
    required this.accessToken,
    required this.refreshToken,
    required this.tokenType,
  });

  factory TokenModel.fromJson(Map<String, dynamic> json) {
    return TokenModel(
      accessToken: json['access_token'],
      refreshToken: json['refresh_token'],
      tokenType: json['token_type'] ?? 'bearer',
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'access_token': accessToken,
      'refresh_token': refreshToken,
      'token_type': tokenType,
    };
  }
}
