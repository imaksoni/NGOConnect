import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:file_picker/file_picker.dart';
import 'package:dio/dio.dart';
import '../providers/channel_provider.dart';
import '../providers/message_provider.dart';

class ChannelDetailScreen extends ConsumerStatefulWidget {
  final String channelId;

  const ChannelDetailScreen({super.key, required this.channelId});

  @override
  ConsumerState<ChannelDetailScreen> createState() =>
      _ChannelDetailScreenState();
}

class _ChannelDetailScreenState extends ConsumerState<ChannelDetailScreen> {
  final TextEditingController _controller = TextEditingController();

  Future<void> _sendMessage() async {
    final text = _controller.text.trim();
    if (text.isEmpty) return;

    final repo = ref.read(messageRepositoryProvider);
    try {
      await repo.createMessage(widget.channelId, text);
      _controller.clear();
      // Notice: We removed the invalidate() here because the WebSocket broadcast
      // will automatically push the new message to our state.
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(
          context,
        ).showSnackBar(SnackBar(content: Text('Failed to send message: $e')));
      }
    }
  }

  bool _isUploading = false;
  double _uploadProgress = 0.0;

  Future<void> _pickAndUploadFile() async {
    try {
      final result = await FilePicker.pickFiles(type: FileType.any);
      if (result == null || result.files.isEmpty) return;

      final file = result.files.first;
      if (file.path == null) {
        throw Exception("File path not found");
      }

      setState(() {
        _isUploading = true;
        _uploadProgress = 0.0;
      });

      final repo = ref.read(messageRepositoryProvider);
      final multipartFile = await MultipartFile.fromFile(
        file.path!,
        filename: file.name,
      );

      final text = _controller.text.trim();

      await repo.uploadAttachment(
        widget.channelId,
        multipartFile,
        content: text,
        onSendProgress: (count, total) {
          setState(() {
            _uploadProgress = count / total;
          });
        },
      );

      _controller.clear();
      // Also no invalidate here; the backend will broadcast the new message.
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(
          context,
        ).showSnackBar(SnackBar(content: Text('Failed to upload file: $e')));
      }
    } finally {
      if (mounted) {
        setState(() {
          _isUploading = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final channelState = ref.watch(channelDetailProvider(widget.channelId));
    final messagesState = ref.watch(messagesProvider(widget.channelId));

    return Scaffold(
      appBar: AppBar(
        title: channelState.when(
          data: (channel) => Text(channel.name),
          loading: () => const Text('Loading...'),
          error: (_, _) => const Text('Error'),
        ),
      ),
      body: Column(
        children: [
          Expanded(
            child: messagesState.when(
              data: (messages) {
                if (messages.isEmpty) {
                  return const Center(child: Text('No messages yet.'));
                }
                return ListView.builder(
                  reverse:
                      true, // typical chat UI, though currently API returns newest first
                  itemCount: messages.length,
                  itemBuilder: (context, index) {
                    final msg = messages[index];
                    return ListTile(
                      title: Text(msg.content),
                      subtitle: Text(msg.senderId ?? 'Unknown User'),
                      trailing: msg.attachments.isNotEmpty
                          ? const Icon(Icons.attachment)
                          : null,
                    );
                  },
                );
              },
              loading: () => const Center(child: CircularProgressIndicator()),
              error: (error, _) => Center(child: Text('Error: $error')),
            ),
          ),
          if (_isUploading) LinearProgressIndicator(value: _uploadProgress),
          SafeArea(
            child: Padding(
              padding: const EdgeInsets.all(8.0),
              child: Row(
                children: [
                  IconButton(
                    icon: const Icon(Icons.attach_file),
                    onPressed: _isUploading ? null : _pickAndUploadFile,
                  ),
                  Expanded(
                    child: TextField(
                      controller: _controller,
                      decoration: const InputDecoration(
                        hintText: 'Type a message...',
                        border: OutlineInputBorder(),
                      ),
                      onSubmitted: _isUploading ? null : (_) => _sendMessage(),
                      enabled: !_isUploading,
                    ),
                  ),
                  IconButton(
                    icon: const Icon(Icons.send),
                    onPressed: _isUploading ? null : _sendMessage,
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}
