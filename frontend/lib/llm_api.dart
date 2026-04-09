import 'dart:convert';

import 'package:http/http.dart' as http;

abstract class LlmApi {
  Future<String> sendPrompt(String prompt);
}

class HttpLlmApi implements LlmApi {
  HttpLlmApi({http.Client? client, String? baseUrl})
    : _client = client ?? http.Client(),
      _baseUrl = baseUrl ?? 'http://127.0.0.1:8000';

  final http.Client _client;
  final String _baseUrl;

  @override
  Future<String> sendPrompt(String prompt) async {
    final response = await _client.put(
      Uri.parse('$_baseUrl/llm'),
      headers: const {'Content-Type': 'application/json'},
      body: jsonEncode({'prompt': prompt}),
    );

    final decoded = jsonDecode(response.body) as Map<String, dynamic>;
    return decoded['response'] as String;
  }
}
