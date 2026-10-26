import 'dart:convert';

import 'package:crypto_safety_scanner/services/api_client.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';

void main() {
  test('wallet scan sends credentials and parses provider evidence', () async {
    final address = '0x${List.filled(40, 'a').join()}';
    final client = ScannerApiClient(
      baseUrl: 'https://scanner.example',
      client: MockClient((request) async {
        expect(request.url.path, '/v1/scan/wallet');
        expect(request.headers['Authorization'], 'Bearer test-token');
        expect(jsonDecode(request.body), {
          'chain': 'ethereum',
          'address': address,
        });
        return http.Response(jsonEncode({
          'score': 90,
          'risk': 'CRITICAL',
          'confidence': 'HIGH',
          'status': 'KNOWN_SCAM',
          'engine_version': '1.0.0',
          'evidence': [
            {
              'code': 'KNOWN_SCAM',
              'severity': 'critical',
              'message': 'Listed address.',
              'source': 'internal',
            },
          ],
        }), 200);
      }),
    );
    addTearDown(client.dispose);

    final result = await client.scanWallet(
      token: 'test-token', chain: 'ethereum', address: ' $address ',
    );
    expect(result.score, 90);
    expect(result.status, 'KNOWN_SCAM');
    expect(result.evidence.single.code, 'KNOWN_SCAM');
  });

  test('quota response preserves the server error', () async {
    final client = ScannerApiClient(
      baseUrl: 'https://scanner.example',
      client: MockClient((_) async => http.Response(
        '{"detail":"Daily scan limit reached"}', 429,
      )),
    );
    addTearDown(client.dispose);
    await expectLater(
      client.scanWallet(token: 'test-token', chain: 'ethereum', address: '0x123'),
      throwsA(isA<ApiException>()
        .having((error) => error.statusCode, 'statusCode', 429)
        .having((error) => error.message, 'message', 'Daily scan limit reached')),
    );
  });

  test('non-object success response is rejected', () async {
    final client = ScannerApiClient(
      baseUrl: 'https://scanner.example',
      client: MockClient((_) async => http.Response('[]', 200)),
    );
    addTearDown(client.dispose);
    await expectLater(
      client.scanWallet(token: 'test-token', chain: 'ethereum', address: '0x123'),
      throwsA(isA<ApiException>()
        .having((error) => error.statusCode, 'statusCode', 502)),
    );
  });
}
