import 'package:flutter/material.dart';

import 'green_theme.dart';
import 'llm_api.dart';

void main() {
  runApp(const ChatApp());
}

class ChatApp extends StatelessWidget {
  const ChatApp({super.key, this.api = const _DefaultLlmApi()});

  final LlmApi api;

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

  final LlmApi api;

  @override
  State<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  final List<Map<String, String>> messages = [];
  final TextEditingController controller = TextEditingController();
  final ScrollController scrollController = ScrollController();
  bool isLoading = false;

  Future<void> sendMessage() async {
    final userMessage = controller.text.trim();
    if (userMessage.isEmpty || isLoading) return;

    setState(() {
      messages.add({'role': 'user', 'text': userMessage});
      isLoading = true;
    });

    controller.clear();
    scrollToBottom();

    try {
      final response = await widget.api.sendPrompt(userMessage);
      if (!mounted) return;

      setState(() {
        messages.add({'role': 'bot', 'text': response});
        isLoading = false;
      });
    } catch (_) {
      if (!mounted) return;

      setState(() {
        messages.add({
          'role': 'bot',
          'text':
              "An error occurred while connecting to the backend FastAPI server.",
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

  Widget buildMessage(Map<String, String> message) {
    final isUser = message['role'] == 'user';

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      alignment: isUser ? Alignment.centerRight : Alignment.centerLeft,
      child: Container(
        constraints: const BoxConstraints(maxWidth: 250),
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: isUser
              ? Theme.of(context).colorScheme.primaryContainer
              : Theme.of(context).colorScheme.surfaceContainerHighest,
          borderRadius: BorderRadius.circular(12),
        ),
        child: Text(message['text'] ?? ''),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('AI Chatbot')),
      body: Column(
        children: [
          Expanded(
            child: Column(
              children: [
                Expanded(
                  child: ListView.builder(
                    controller: scrollController,
                    itemCount: messages.length,
                    itemBuilder: (context, index) {
                      return buildMessage(messages[index]);
                    },
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
                      decoration: const InputDecoration(
                        hintText: 'Type a message...',
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

class _DefaultLlmApi implements LlmApi {
  const _DefaultLlmApi();

  @override
  Future<String> sendPrompt(String prompt) {
    return HttpLlmApi().sendPrompt(prompt);
  }
}
