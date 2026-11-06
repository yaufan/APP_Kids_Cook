import 'dart:math' as math;

/// The animal customers (assets/art/customers/).
enum Customer {
  bear('小熊'),
  rabbit('小兔'),
  cat('小貓'),
  pig('小豬'),
  duck('小鴨');

  const Customer(this.zh);

  final String zh;
}

/// How much counting a parent wants: 3–4 year olds count to about five,
/// 5–6 year olds further and follow longer patterns.
enum Level { little, big }

/// What kind of little game a step is (features/kitchen/steps.dart).
enum StepKind {
  /// Rub over the thing: hands with soap, a tomato under the tap, a shaker.
  rub,

  /// Swipe across each dashed line, counting the pieces.
  cut,

  /// Tap the thing at the side, one at a time, into the bowl, cup or pot.
  tapIn,

  /// Draw circles in the bowl.
  stir,

  /// Hold to pour, let go at the line.
  pour,

  /// Wait for the colour, then swipe up to flip.
  cook,

  /// Ask a grown-up: the fire, the boiling water.
  adult,

  /// Put things on in the order the card shows (a stack or a pattern).
  build,

  /// Wrap each dumpling: filling in, pinch shut.
  wrap,

  /// Wait for the dumplings to float, then scoop them out.
  boil,

  /// Tap the things to finish: sauce, a lid, a straw.
  finish,

  /// Swipe sideways to roll.
  roll,
}

/// One step of a recipe, with what it shows and says.
class CookStep {
  const CookStep(this.kind, this.zh, {this.art = '', this.target = '', this.result = '', this.count = 0, this.sequence = const [], this.sfx = '', this.en = ''});

  final StepKind kind;

  /// What is said (and printed small under the picture).
  final String zh;

  /// The thing being worked on (assets/art/<art>.svg).
  final String art;

  /// Where things go (a bowl, a cup, a pot, a plate).
  final String target;

  /// What it looks like afterwards.
  final String result;

  /// How many (pieces, eggs, scoops): 0 when nothing is counted.
  final int count;

  /// [StepKind.build]: the pieces in order.
  final List<String> sequence;

  /// The sound of each action (assets/sounds/).
  final String sfx;

  /// The English word for the thing, when a parent turns English on.
  final String en;

  /// The picture on the recipe card.
  String get icon => kind == StepKind.rub && art == 'ui/hands_wash' ? 'ui/hands_wash' : (result.isNotEmpty && kind != StepKind.tapIn ? result : art);
}

/// A dish on the menu.
class Dish {
  const Dish({required this.id, required this.zh, required this.en, required this.customer, required this.counted, required this.countedZh, required this.little, required this.big, required this.steps});

  final String id;
  final String zh;
  final String en;
  final Customer customer;

  /// The thing the order asks a number of (assets/art/food/).
  final String counted;
  final String countedZh;

  /// How many the order can ask for, by level (inclusive).
  final (int, int) little;
  final (int, int) big;
  final List<CookStep> Function(int n, Level level) steps;

  String get icon => 'dishes/$id';

  int countFor(Level level, math.Random r) {
    final (lo, hi) = level == Level.little ? little : big;
    return lo + r.nextInt(hi - lo + 1);
  }
}

const _washHands = CookStep(StepKind.rub, '先洗手，搓出泡泡', art: 'ui/hands_wash', sfx: 'wash');

/// The five dishes of 0.1 (docs/design.md "0.1 的五道菜和步驟").
final dishes = <Dish>[
  Dish(
    id: 'sandwich',
    zh: '番茄起司三明治',
    en: 'sandwich',
    customer: Customer.bear,
    counted: 'food/tomato_slice',
    countedZh: '片番茄',
    little: (2, 3),
    big: (3, 5),
    steps: (n, _) => [
      _washHands,
      const CookStep(StepKind.rub, '把番茄洗乾淨', art: 'food/tomato', target: 'tools/sink', sfx: 'water', en: 'tomato'),
      CookStep(StepKind.cut, '切番茄，切 $n 片', art: 'food/tomato', target: 'tools/cutting_board', result: 'food/tomato_slice', count: n, sfx: 'chop', en: 'tomato'),
      CookStep(StepKind.build, '疊起來：麵包、起司、$n 片番茄、麵包', target: 'tools/plate', sequence: [
        'food/bread',
        'food/cheese',
        for (var i = 0; i < n; i++) 'food/tomato_slice',
        'food/bread',
      ], sfx: 'pop', en: 'sandwich'),
      const CookStep(StepKind.cut, '切成三角形', art: 'food/bread', target: 'tools/cutting_board', result: 'food/sandwich', count: 1, sfx: 'chop'),
    ],
  ),
  Dish(
    id: 'fruit_skewer',
    zh: '水果串',
    en: 'fruit skewer',
    customer: Customer.rabbit,
    counted: 'food/banana_piece',
    countedZh: '塊香蕉',
    little: (2, 3),
    big: (3, 4),
    steps: (n, level) => [
      _washHands,
      const CookStep(StepKind.rub, '把草莓洗乾淨', art: 'food/strawberry', target: 'tools/sink', sfx: 'water', en: 'strawberry'),
      CookStep(StepKind.cut, '切香蕉，切 $n 塊', art: 'food/banana', target: 'tools/cutting_board', result: 'food/banana_piece', count: n, sfx: 'chop', en: 'banana'),
      CookStep(StepKind.build, '照順序串起來', target: 'food/skewer', sequence: [
        for (var i = 0; i < n; i++) ...[
          'food/strawberry',
          'food/banana_piece',
          if (level == Level.big) 'food/grape',
        ],
      ], sfx: 'pop', en: 'fruit'),
    ],
  ),
  Dish(
    id: 'danbing',
    zh: '蛋餅',
    en: 'egg pancake',
    customer: Customer.cat,
    counted: 'food/egg',
    countedZh: '顆蛋',
    little: (1, 2),
    big: (2, 3),
    steps: (n, _) => [
      _washHands,
      CookStep(StepKind.tapIn, '打 $n 顆蛋', art: 'food/egg', target: 'tools/bowl', result: 'tools/bowl_egg', count: n, sfx: 'crack', en: 'egg'),
      const CookStep(StepKind.stir, '攪一攪，畫圈圈', art: 'tools/bowl_egg', sfx: 'stir'),
      const CookStep(StepKind.adult, '開火要請大人幫忙', art: 'tools/stove'),
      const CookStep(StepKind.pour, '把蛋倒進鍋子', art: 'tools/bowl_egg', target: 'tools/pan', result: 'food/batter_raw', sfx: 'pour'),
      const CookStep(StepKind.cook, '等蛋變金黃色，再往上滑翻面', art: 'food/batter_raw', target: 'tools/pan', result: 'food/batter_cooked', sfx: 'sizzle'),
      const CookStep(StepKind.roll, '往旁邊滑，捲起來', art: 'food/crepe', result: 'food/danbing_roll', sfx: 'flip'),
      const CookStep(StepKind.cut, '切成 4 塊', art: 'food/danbing_roll', target: 'tools/cutting_board', result: 'food/danbing_pieces', count: 4, sfx: 'chop'),
      const CookStep(StepKind.finish, '淋上醬油膏', art: 'food/soy_paste', target: 'food/danbing_pieces', sequence: ['food/soy_paste'], sfx: 'squeeze'),
    ],
  ),
  Dish(
    id: 'milk_tea',
    zh: '珍珠奶茶',
    en: 'bubble tea',
    customer: Customer.duck,
    counted: 'food/pearls',
    countedZh: '匙珍珠',
    little: (1, 3),
    big: (3, 5),
    steps: (n, level) => [
      CookStep(StepKind.tapIn, '舀 $n 匙珍珠', art: 'food/pearls', target: 'tools/cup', result: 'food/pearl', count: n, sfx: 'plop', en: 'pearls'),
      CookStep(StepKind.tapIn, '放 ${level == Level.little ? 2 : 4} 顆冰塊', art: 'food/ice', target: 'tools/cup', result: 'food/ice', count: level == Level.little ? 2 : 4, sfx: 'plop', en: 'ice'),
      const CookStep(StepKind.pour, '倒茶，倒到線就放開', art: 'food/tea', target: 'tools/cup', sfx: 'pour', en: 'tea'),
      const CookStep(StepKind.rub, '搖一搖', art: 'tools/cup', sfx: 'shake'),
      const CookStep(StepKind.finish, '蓋上蓋子，插上吸管', art: 'tools/cup', target: 'tools/cup', sequence: ['tools/lid', 'tools/straw'], result: 'food/milk_tea', sfx: 'pop'),
    ],
  ),
  Dish(
    id: 'dumplings',
    zh: '水餃',
    en: 'dumplings',
    customer: Customer.pig,
    counted: 'food/dumpling',
    countedZh: '顆水餃',
    little: (2, 3),
    big: (4, 6),
    steps: (n, _) => [
      _washHands,
      CookStep(StepKind.wrap, '包 $n 顆水餃：放餡，再捏起來', art: 'food/wrapper', target: 'tools/tray', result: 'food/dumpling', count: n, sfx: 'pinch', en: 'dumpling'),
      const CookStep(StepKind.adult, '燒開水要請大人幫忙', art: 'tools/pot'),
      CookStep(StepKind.tapIn, '一顆一顆放進鍋子', art: 'food/dumpling', target: 'tools/pot_boil', result: 'food/dumpling', count: n, sfx: 'plop'),
      CookStep(StepKind.boil, '等水餃浮起來，再撈起來', art: 'food/dumpling', target: 'tools/pot_boil', result: 'food/dumplings_plate', count: n, sfx: 'boil'),
    ],
  ),
];

Dish? dishById(String id) => dishes.where((d) => d.id == id).firstOrNull;

/// A customer's order: the dish and how many of its counted thing.
class Order {
  const Order(this.dish, this.count);

  final Dish dish;
  final int count;

  List<CookStep> get steps => dish.steps(count, Level.little);

  List<CookStep> stepsFor(Level level) => dish.steps(count, level);
}
