import '../core/dishes.dart';

/// Everything the app says, in Traditional Chinese (Taiwan).
abstract final class Strings {
  static const appName = '動物小餐廳';

  // The restaurant.
  static const start = '開始做';
  static const book = '食譜書';
  static const parent = '家長';
  static const coins = '金幣';
  static const stars = '星星';
  static String welcome(Customer c) => '歡迎光臨！${c.zh}來了';
  static String order(Order o) => '我想要${o.dish.zh}，要 ${o.count} ${o.dish.countedZh}';
  static String orderShort(Order o) => '${o.dish.zh}（${o.count} ${o.dish.countedZh}）';
  static const yum = '好好吃！謝謝你！';
  static String earned(int coins) => '得到 $coins 個金幣和 1 顆星星';
  static const nextCustomer = '下一位客人';

  // The kitchen.
  static const kitchen = '廚房';
  static const back = '回去';
  static const doneStep = '做好了！';
  static const dishDone = '完成了！';
  static const serve = '端給客人';
  static const count = ['零', '一', '二', '三', '四', '五', '六', '七', '八', '九', '十'];
  static String countZh(int n) => n <= 10 ? count[n] : '$n';
  static const countEn = ['zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten'];
  static const rubMore = '再搓一搓';
  static const cutHere = '沿著虛線切下去';
  static const tapIn = '點一下，放進去';
  static const stirMore = '畫圈圈，攪一攪';
  static const holdToPour = '按住倒進去，到線就放開';
  static const justRight = '剛剛好！';
  static const tooMuch = '多了一點點，沒關係！';
  static const notYet = '還沒好喔，再等一下';
  static const flipNow = '變金黃色了！往上滑翻面';
  static const adultHere = '大人來幫忙了';
  static const adultSafety = '爐火和熱水很燙，要請大人幫忙喔';
  static const nextOne = '下一個是什麼呢？';
  static String putThis(String what) => '先放$what喔';
  static const wrapFill = '點餡料，放到皮上';
  static const wrapPinch = '捏一捏，把水餃捏起來';
  static const waitFloat = '等水餃浮起來';
  static const floated = '浮起來了！撈起來';
  static const rollIt = '往旁邊滑，捲起來';

  /// Food names for "先放…喔" and English words.
  static String foodName(String art) => const {
        'food/bread': '麵包',
        'food/cheese': '起司',
        'food/tomato_slice': '番茄',
        'food/strawberry': '草莓',
        'food/banana_piece': '香蕉',
        'food/grape': '葡萄',
        'tools/lid': '蓋子',
        'tools/straw': '吸管',
        'food/soy_paste': '醬油膏',
      }[art] ??
      '';

  // The recipe book.
  static String timesCooked(int n) => n == 0 ? '還沒做過' : '做過 $n 次';
  static String steps(int n) => '$n 個步驟';

  // Parent gate (as in the sibling apps).
  static const callParent = '請爸爸媽媽來幫忙喔！';
  static const parentGateTitle = '家長確認';
  static String gateQuestion(String a, String b) => '$a 加 $b 等於多少？';
  static const gateRules = '答錯三次要等一分鐘。';
  static const wrongAnswer = '不對喔，換一題。';
  static String gateWait(int s) => '請等 $s 秒再試';
  static const backspace = '刪掉';
  static const cancel = '取消';

  // Parent mode.
  static const parentTitle = '家長模式';
  static const progress = '進度';
  static String servedLine(int n, int coins) => '端給客人 $n 次，金幣 $coins 個';
  static const level = '難度';
  static String levelName(Level l) => switch (l) {
        Level.little => '3～4 歲（數到 5）',
        Level.big => '5～6 歲（數得更多、規律更長）',
      };
  static const english = '念英文（番茄 tomato）';
  static const sound = '聲音';
  static const music = '背景音樂';
  static const effects = '音效';
  static const voice = '語音（念步驟和數數）';
  static const together = '一起做做看（真的食譜）';
  static const togetherNote = '週末可以和小朋友在家裡真的做一次。都不用開火；刀子用兒童安全刀，大人在旁邊。';
  static const realRecipes = [
    ('水果串', '香蕉、草莓、葡萄洗乾淨；香蕉切塊；照順序串在竹籤上（竹籤尖端大人先剪平）。'),
    ('番茄起司三明治', '吐司兩片、起司一片、番茄切片；照順序疊起來，用兒童刀對角切成三角形。'),
    ('優格水果杯', '無糖優格放進杯子，上面放切好的水果，撒一點堅果碎（三歲以下不要放整顆堅果）。'),
    ('飯糰', '白飯放在保鮮膜上，包一點肉鬆或玉米，用保鮮膜捏成三角形。'),
  ];
  static const edition = '版本';
  static const fullNote = '免費：餐廳和 5 道菜。完整版（一次買斷）：全部食譜、市場、菜園、節日料理、餐廳裝飾。測試版先全部打開。';
  static const fullTest = '完整版（測試版的開關）';
  static const about = '關於';
  static String version(String v) => '動物小餐廳 $v';
  static const privacy = '不連網、不定位、沒有廣告、沒有帳號。資料只存在這支手機裡。';
}
