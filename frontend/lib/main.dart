import 'package:flutter/material.dart';

import 'green_theme.dart';
import 'llm_api.dart';

void main() {
  runApp(ChatApp(api: QaApi()));
}

class ChatApp extends StatelessWidget {
  const ChatApp({super.key, required this.api});

  final QaApi api;

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'AI Chatbot',
      theme: GreenTheme().greenTheme,
      darkTheme: GreenTheme().darkGreenTheme,
      home: ChatScreen(api: api),
    );
  }
}

class ChatScreen extends StatefulWidget {
  const ChatScreen({super.key, required this.api});

  final QaApi api;

  @override
  State<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  // Each message: role, text, and optional metadata (type, score, confidence)
  final List<Map<String, dynamic>> messages = [];
  final TextEditingController controller = TextEditingController();
  final ScrollController scrollController = ScrollController();
  bool isLoading = false;

  // Set when the bot asked a clarifying question — next user message goes to /clarify
  String? _pendingSessionId;

  Future<void> sendMessage() async {
    final userText = controller.text.trim();
    if (userText.isEmpty || isLoading) return;

    setState(() {
      messages.add({'role': 'user', 'text': userText});
      isLoading = true;
    });
    controller.clear();
    scrollToBottom();

    try {
      if (_pendingSessionId != null) {
        final result = await widget.api.clarify(_pendingSessionId!, userText);
        setState(() {
          _pendingSessionId = null;
          messages.add({
            'role': 'bot',
            'text': result.finalAnswer,
            'type': 'final',
            'confidence': result.confidence,
          });
          isLoading = false;
        });
      } else {
        final result = await widget.api.ask(userText);
        setState(() {
          if (result.decision == 'answer') {
            messages.add({
              'role': 'bot',
              'text': result.answer ?? '',
              'type': 'answer',
              'score': result.uncertaintyScore,
            });
          } else {
            _pendingSessionId = result.sessionId;
            messages.add({
              'role': 'bot',
              'text': result.clarifyingQuestion ?? '',
              'type': 'clarifying',
              'score': result.uncertaintyScore,
            });
          }
          isLoading = false;
        });
      }
    } catch (e) {
      setState(() {
        messages.add({
          'role': 'bot',
          'text': 'Error connecting to backend: $e',
          'type': 'error',
        });
        isLoading = false;
      });
    }

    scrollToBottom();
  }

  void scrollToBottom() {
    Future.delayed(const Duration(milliseconds: 100), () {
      if (!scrollController.hasClients) return;
      scrollController.animateTo(
        scrollController.position.maxScrollExtent,
        duration: const Duration(milliseconds: 300),
        curve: Curves.easeOut,
      );
    });
  }

  Widget buildMessage(Map<String, dynamic> msg) {
    final isUser = msg['role'] == 'user';
    final type = msg['type'] as String?;
    final score = msg['score'] as double?;
    final confidence = msg['confidence'] as double?;

    String? badge;
    if (type == 'clarifying' && score != null) {
      badge = 'Needs clarification  •  uncertainty ${score.toStringAsFixed(2)}';
    } else if (type == 'answer' && score != null) {
      badge = 'Direct answer  •  uncertainty ${score.toStringAsFixed(2)}';
    } else if (type == 'final' && confidence != null) {
      badge = 'Final answer  •  confidence ${confidence.toStringAsFixed(2)}';
    }

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      alignment: isUser ? Alignment.centerRight : Alignment.centerLeft,
      child: Column(
        crossAxisAlignment:
            isUser ? CrossAxisAlignment.end : CrossAxisAlignment.start,
        children: [
          Container(
            constraints: const BoxConstraints(maxWidth: 320),
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: isUser
                  ? Theme.of(context).colorScheme.primaryContainer
                  : Theme.of(context).colorScheme.surfaceContainerHighest,
              borderRadius: BorderRadius.circular(12),
            ),
            child: Text(msg['text'] as String? ?? ''),
          ),
          if (badge != null)
            Padding(
              padding: const EdgeInsets.only(top: 3, left: 4, right: 4),
              child: Text(
                badge,
                style: Theme.of(context).textTheme.labelSmall?.copyWith(
                  color: type == 'clarifying'
                      ? Colors.orange.shade700
                      : Colors.green.shade700,
                ),
              ),
            ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('AI Chatbot'),
        bottom: _pendingSessionId != null
            ? PreferredSize(
                preferredSize: const Size.fromHeight(24),
                child: Container(
                  color: Colors.orange.shade100,
                  width: double.infinity,
                  padding: const EdgeInsets.symmetric(
                    horizontal: 12,
                    vertical: 4,
                  ),
                  child: Text(
                    'Awaiting your clarification…',
                    style: TextStyle(
                      fontSize: 12,
                      color: Colors.orange.shade900,
                    ),
                  ),
                ),
              )
            : null,
      ),
      body: Column(
        children: [
          Expanded(
            child: Column(
              children: [
                Expanded(
                  child: ListView.builder(
                    controller: scrollController,
                    itemCount: messages.length,
                    itemBuilder: (context, index) =>
                        buildMessage(messages[index]),
                  ),
                ),
                if (isLoading)
                  const Padding(
                    padding: EdgeInsets.only(bottom: 8),
                    child: Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        SizedBox(
                          width: 18,
                          height: 18,
                          child: CircularProgressIndicator(strokeWidth: 2),
                        ),
                        SizedBox(width: 10),
                        Text('Thinking...'),
                      ],
                    ),
                  ),
              ],
            ),
          ),
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 8),
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 8),
              decoration: BoxDecoration(
                color: Colors.white,
                border: Border.all(color: Colors.grey, width: 0.5),
                borderRadius: BorderRadius.circular(8),
              ),
              child: Row(
                children: [
                  Expanded(
                    child: TextField(
                      controller: controller,
                      enabled: !isLoading,
                      decoration: InputDecoration(
                        hintText: _pendingSessionId != null
                            ? 'Answer the clarifying question…'
                            : 'Type a message...',
                        border: InputBorder.none,
                      ),
                      onSubmitted: (_) => sendMessage(),
                    ),
                  ),
                  IconButton(
                    icon: isLoading
                        ? const SizedBox(
                            width: 20,
                            height: 20,
                            child: CircularProgressIndicator(strokeWidth: 2),
                          )
                        : const Icon(Icons.send),
                    onPressed: isLoading ? null : sendMessage,
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 10),
        ],
      ),
    );
  }
}
