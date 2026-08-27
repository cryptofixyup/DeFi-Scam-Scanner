import 'package:flutter/material.dart';

import '../l10n/app_localizations.dart';
import '../models/scan_result.dart';
import '../services/api_client.dart';
import 'result_screen.dart';

class ScanScreen extends StatefulWidget {
  final ScannerApiClient api;
  final String accessToken;

  const ScanScreen({super.key, required this.api, required this.accessToken});

  @override
  State<ScanScreen> createState() => _ScanScreenState();
}

class _ScanScreenState extends State<ScanScreen> {
  final _controller = TextEditingController();
  bool _loading = false;
  String? _error;

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  Future<void> _scan() async {
    final address = _controller.text.trim();
    final l10n = AppLocalizations.of(context)!;
    if (!RegExp(r'^0x[0-9a-fA-F]{40}$').hasMatch(address)) {
      setState(() => _error = l10n.invalidAddress);
      return;
    }

    setState(() {
      _loading = true;
      _error = null;
    });

    try {
      final result = await widget.api.scanWallet(
        token: widget.accessToken,
        chain: 'ethereum',
        address: address,
      );
      if (!mounted) return;
      await Navigator.of(context).push(
        MaterialPageRoute(builder: (_) => ResultScreen(result: result)),
      );
    } on ApiException catch (e) {
      if (mounted) setState(() => _error = e.message);
    } catch (_) {
      if (mounted) setState(() => _error = l10n.scanFailed);
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    return Scaffold(
      appBar: AppBar(title: Text(l10n.appName)),
      body: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          Text(l10n.checkBeforeTrust, style: Theme.of(context).textTheme.headlineSmall),
          const SizedBox(height: 20),
          TextField(
            controller: _controller,
            autocorrect: false,
            enableSuggestions: false,
            keyboardType: TextInputType.text,
            decoration: InputDecoration(
              labelText: l10n.walletAddress,
              hintText: '0x...',
              border: const OutlineInputBorder(),
            ),
          ),
          const SizedBox(height: 12),
          if (_error != null)
            Text(_error!, style: TextStyle(color: Theme.of(context).colorScheme.error)),
          const SizedBox(height: 12),
          FilledButton(
            onPressed: _loading ? null : _scan,
            child: _loading
                ? const SizedBox(width: 20, height: 20, child: CircularProgressIndicator(strokeWidth: 2))
                : Text(l10n.scan),
          ),
        ],
      ),
    );
  }
}
