import 'dart:convert';

import 'package:http/http.dart' as http;

import '../models/scan_result.dart';

class ApiException implements Exception {
  final int statusCode;
  final String message;

  const ApiException(this.statusCode, this.message);

  @override
  String toString() => 'ApiException($statusCode): $message';
}

class ScannerApiClient {
  final String baseUrl;
  final http.Client _client;

  ScannerApiClient({required this.baseUrl, http.Client? client})
      : _client = client ?? http.Client();

  Future<ScanResult> scanWallet({
    required String token,
    required String chain,
    required String address,
  }) async {
    final response = await _client
        .post(
          Uri.parse('$baseUrl/v1/scan/wallet'),
          headers: {
            'Authorization': 'Bearer $token',
            'Content-Type': 'application/json',
          },
          body: jsonEncode({
            'chain': chain,
            'address': address.trim(),
          }),
        )
        .timeout(const Duration(seconds: 8));

    if (response.statusCode < 200 || response.statusCode >= 300) {
      String message = 'Scan failed.';
      try {
        final body = jsonDecode(response.body);
        if (body is Map<String, dynamic> && body['detail'] is String) {
          message = body['detail'] as String;
        }
      } catch (_) {}
      throw ApiException(response.statusCode, message);
    }

    final body = jsonDecode(response.body);
    if (body is! Map<String, dynamic>) {
      throw const ApiException(502, 'Invalid server response.');
    }
    return ScanResult.fromJson(body);
  }

  void dispose() => _client.close();
}
