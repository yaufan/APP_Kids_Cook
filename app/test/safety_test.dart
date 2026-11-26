import 'dart:io';

import 'package:flutter_test/flutter_test.dart';
import 'package:animal_restaurant/features/parent/parent_gate.dart';

import 'helpers.dart';

/// Privacy and the parent gate: no network, no pages opened by other apps,
/// parent mode only through the gate.
void main() {
  test('the app asks for no network and takes no links from other apps', () {
    final manifest = File('android/app/src/main/AndroidManifest.xml').readAsStringSync();
    expect(manifest, isNot(contains('android.permission.INTERNET')));
    expect(manifest, contains('android:name="flutter_deeplinking_enabled" android:value="false"'));
    expect(File('ios/Runner/Info.plist').readAsStringSync(), contains('<key>FlutterDeepLinkingEnabled</key>\n\t<false/>'));
  });

  test('the phone\'s own speech can be reached on Android 11+, and nothing goes into backups', () {
    final manifest = File('android/app/src/main/AndroidManifest.xml').readAsStringSync();
    expect(manifest, contains('<action android:name="android.intent.action.TTS_SERVICE" />'));
    expect(manifest, contains('android:allowBackup="false"'));
    expect(manifest, contains('android:fullBackupContent="false"'));
    expect(manifest, contains('android:dataExtractionRules="@xml/data_extraction_rules"'));
    final rules = File('android/app/src/main/res/xml/data_extraction_rules.xml').readAsStringSync();
    for (final where in ['cloud-backup', 'device-transfer']) {
      final part = RegExp('<$where>(.*?)</$where>', dotAll: true).firstMatch(rules)!.group(1)!;
      for (final domain in ['root', 'file', 'database', 'sharedpref', 'external']) {
        expect(part, contains('<exclude domain="$domain" path="." />'), reason: '$where $domain');
      }
    }
  });

  test('the build checks the packages ask for no camera, microphone, contacts, photos or location', () {
    for (final workflow in ['app.yml', 'release.yml']) {
      final check = RegExp(r"grep -E '([^']+)' permissions.txt").firstMatch(File('../.github/workflows/$workflow').readAsStringSync())!.group(1)!;
      for (final p in ['INTERNET', 'LOCATION', 'AD_ID', 'CAMERA', 'RECORD_AUDIO', 'READ_CONTACTS', 'READ_MEDIA_', 'READ_EXTERNAL_STORAGE']) {
        expect(check.split('|'), contains(p), reason: '$workflow $p');
      }
    }
  });

  testWidgets('parent mode cannot be opened without the gate', (tester) async {
    final app = await TestApp.start(tester);
    app.go('/parent');
    await app.settle();
    expect(app.location, '/', reason: 'no pass from the gate');
    ParentPass.grant();
    app.go('/parent');
    await app.settle();
    expect(app.location, '/parent', reason: 'right after the gate');
    app.go('/');
    await app.settle();
    app.go('/parent');
    await app.settle();
    expect(app.location, '/', reason: 'the pass is used up');
    await app.end();
  });
}
