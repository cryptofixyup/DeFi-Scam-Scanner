import 'package:flutter/material.dart';

import '../l10n/app_localizations.dart';
import '../models/scan_result.dart';

class ResultScreen extends StatelessWidget {
  final ScanResult result;

  const ResultScreen({super.key, required this.result});

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    final score = result.score;
    final risk = result.risk.toUpperCase();

    return Scaffold(
      appBar: AppBar(title: Text(l10n.scanResult)),
      body: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          Text(
            score == null ? risk : '$risk\n$score / 100',
            style: Theme.of(context).textTheme.displaySmall?.copyWith(fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 12),
          Text('${l10n.confidence}: ${result.confidence}'),
          const SizedBox(height: 24),
          Text(l10n.findings, style: Theme.of(context).textTheme.titleLarge),
          const SizedBox(height: 8),
          if (result.evidence.isEmpty) Text(l10n.noKnownFlags),
          ...result.evidence.map(
            (item) => Card(
              child: ListTile(
                title: Text(item.message),
                subtitle: Text('${item.code} • ${item.severity} • ${item.source}'),
              ),
            ),
          ),
          const SizedBox(height: 12),
          Text('${l10n.engineVersion}: ${result.engineVersion}'),
          const SizedBox(height: 20),
          Text(l10n.scanDisclaimer),
        ],
      ),
    );
  }
}
