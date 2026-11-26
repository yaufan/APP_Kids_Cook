/// What the voice is given to say: a number before a measure word is
/// written out in characters, and 2 is 「兩」 (兩片番茄, not 二片番茄), so
/// the phone's voice says it the way people do. The screen keeps the
/// numerals; counting one by one (一、二、三) is said as it is.
String spoken(String zh) => zh.replaceAllMapped(RegExp(r'\s*(\d+)\s*(?=[\u4e00-\u9fff])'), (m) => amount(int.parse(m.group(1)!)));

/// [n] as said before a measure word: 一、兩、三……十、十一……
String amount(int n) {
  const digits = ['零', '一', '二', '三', '四', '五', '六', '七', '八', '九'];
  if (n == 2) return '兩';
  if (n < 10) return digits[n];
  if (n < 20) return '十${n == 10 ? '' : digits[n % 10]}';
  if (n < 100) return '${digits[n ~/ 10]}十${n % 10 == 0 ? '' : digits[n % 10]}';
  return '$n';
}
