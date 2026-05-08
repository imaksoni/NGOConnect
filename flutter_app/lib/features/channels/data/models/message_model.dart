class MessageAttachmentModel {
  final String id;
  final String messageId;
  final String fileName;
  final String? contentType;
  final int? fileSize;
  final String storageKey;
  final String? uploadedBy;
  final DateTime createdAt;

  MessageAttachmentModel({
    required this.id,
    required this.messageId,
    required this.fileName,
    this.contentType,
    this.fileSize,
    required this.storageKey,
    this.uploadedBy,
    required this.createdAt,
  });

  factory MessageAttachmentModel.fromJson(Map<String, dynamic> json) {
    return MessageAttachmentModel(
      id: json['id'],
      messageId: json['message_id'],
      fileName: json['file_name'],
      contentType: json['content_type'],
      fileSize: json['file_size'],
      storageKey: json['storage_key'],
      uploadedBy: json['uploaded_by'],
      createdAt: DateTime.parse(json['created_at']),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'message_id': messageId,
      'file_name': fileName,
      'content_type': contentType,
      'file_size': fileSize,
      'storage_key': storageKey,
      'uploaded_by': uploadedBy,
      'created_at': createdAt.toIso8601String(),
    };
  }
}

class MessageModel {
  final String id;
  final String channelId;
  final String? senderId;
  final String content;
  final String? type;
  final DateTime createdAt;
  final DateTime updatedAt;
  final List<MessageAttachmentModel> attachments;

  MessageModel({
    required this.id,
    required this.channelId,
    this.senderId,
    required this.content,
    this.type,
    required this.createdAt,
    required this.updatedAt,
    this.attachments = const [],
  });

  factory MessageModel.fromJson(Map<String, dynamic> json) {
    var list = json['attachments'] as List? ?? [];
    List<MessageAttachmentModel> attachmentsList = list
        .map((i) => MessageAttachmentModel.fromJson(i))
        .toList();

    return MessageModel(
      id: json['id'],
      channelId: json['channel_id'],
      senderId: json['sender_id'],
      content: json['content'],
      type: json['type'],
      createdAt: DateTime.parse(json['created_at']),
      updatedAt: DateTime.parse(json['updated_at']),
      attachments: attachmentsList,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'channel_id': channelId,
      'sender_id': senderId,
      'content': content,
      'type': type,
      'created_at': createdAt.toIso8601String(),
      'updated_at': updatedAt.toIso8601String(),
      'attachments': attachments.map((v) => v.toJson()).toList(),
    };
  }
}
