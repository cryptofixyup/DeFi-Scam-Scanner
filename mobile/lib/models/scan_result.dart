class ScanEvidence {
  final String code;
  final String severity;
  final String message;
  final String source;

  const ScanEvidence({
    required this.code,
    required this.severity,
    required this.message,
    required this.source,
  });

  factory ScanEvidence.fromJson(Map<String, dynamic> json) {
    return ScanEvidence(
      code: json['code'] as String? ?? 'UNKNOWN',
      severity: json['severity'] as String? ?? 'unknown',
      message: json['message'] as String? ?? 'No explanation provided.',
      source: json['source'] as String? ?? 'unknown',
    );
  }
}

class ScanResult {
  final int? score;
  final String risk;
  final String confidence;
  final String status;
  final String engineVersion;
  final List<ScanEvidence> evidence;

  const ScanResult({
    required this.score,
    required this.risk,
    required this.confidence,
    required this.status,
    required this.engineVersion,
    required this.evidence,
  });

  factory ScanResult.fromJson(Map<String, dynamic> json) {
    final raw = json['evidence'];
    final evidence = raw is List
        ? raw
            .whereType<Map<String, dynamic>>()
            .map(ScanEvidence.fromJson)
            .toList(growable: false)
        : const <ScanEvidence>[];

    return ScanResult(
      score: (json['score'] as num?)?.toInt(),
      risk: json['risk'] as String? ?? 'UNKNOWN',
      confidence: json['confidence'] as String? ?? 'LOW',
      status: json['status'] as String? ?? 'INSUFFICIENT_DATA',
      engineVersion: json['engine_version'] as String? ?? 'unknown',
      evidence: evidence,
    );
  }
}
