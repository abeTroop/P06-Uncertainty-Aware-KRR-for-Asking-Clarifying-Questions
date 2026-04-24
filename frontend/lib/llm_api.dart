import 'dart:convert';

import 'package:http/http.dart' as http;

class AskResponse {
  final String sessionId;
  final String decision;
  final double uncertaintyScore;
  final String? answer;
  final String? clarifyingQuestion;

  AskResponse({
    required this.sessionId,
    required this.decision,
    required this.uncertaintyScore,
    this.answer,
    this.clarifyingQuestion,
  });

  factory AskResponse.fromJson(Map<String, dynamic> json) => AskResponse(
    sessionId: json['session_id'] as String,
    decision: json['decision'] as String,
    uncertaintyScore: (json['uncertainty_score'] as num).toDouble(),
    answer: json['answer'] as String?,
    clarifyingQuestion: json['clarifying_question'] as String?,
  );
}

class ClarifyResponse {
  final String finalAnswer;
  final double? confidence;

  ClarifyResponse({required this.finalAnswer, this.confidence});

  factory ClarifyResponse.fromJson(Map<String, dynamic> json) => ClarifyResponse(
    finalAnswer: json['final_answer'] as String,
    confidence: (json['confidence'] as num?)?.toDouble(),
  );
}

class QaApi {
  QaApi({http.Client? client, String? baseUrl})
    : _client = client ?? http.Client(),
      _baseUrl = baseUrl ?? 'http://127.0.0.1:8000';

  final http.Client _client;
  final String _baseUrl;

  Future<AskResponse> ask(String question) async {
    final response = await _client.post(
      Uri.parse('$_baseUrl/ask'),
      headers: const {'Content-Type': 'application/json'},
      body: jsonEncode({'question': question}),
    );
    return AskResponse.fromJson(
      jsonDecode(response.body) as Map<String, dynamic>,
    );
  }

  Future<ClarifyResponse> clarify(
    String sessionId,
    String clarification,
  ) async {
    final response = await _client.post(
      Uri.parse('$_baseUrl/clarify'),
      headers: const {'Content-Type': 'application/json'},
      body: jsonEncode({
        'session_id': sessionId,
        'clarification': clarification,
      }),
    );
    return ClarifyResponse.fromJson(
      jsonDecode(response.body) as Map<String, dynamic>,
    );
  }
}
