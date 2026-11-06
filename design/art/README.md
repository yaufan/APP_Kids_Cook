# 動物小餐廳的圖（黏土風）

這裡的程式畫出 APP 裡所有的圖，寫進 `app/assets/art/`（APP 圖示寫進 `app/android/` 和 `app/ios/`）。全部用 Python 產生 SVG，沒有用別人的素材；每次跑出來都一模一樣（要亂數的地方用固定的種子）。

## 畫風：黏土
照使用者選的草圖「A 黏土風」（`docs/mockups/`）：
- 圓圓胖胖、像捏出來的形狀，**沒有框線**，溫暖的顏色。
- 每一塊黏土：左上亮、右下稍暗；邊緣有一圈「捏圓的邊」（左上白、右下深）；右下有柔和的影子；左上一點亮光；有些地方有淺淺的手指印。
- 站著的東西下面有一小片地上的影子。
- 草圖是用 SVG 濾鏡做出黏土感，但 APP 用的 flutter_svg **不會畫濾鏡**，所以這裡只用它會畫的東西：路徑、漸層、裁切（clipPath）、透明度、`<use>`。沒有 `<filter>`、`<mask>`、CSS、`<foreignObject>`。
- flutter_svg 一張圖最多只能展開 1000 個 `<use>`，`clay.py` 每張圖最多用 850 個，超過的就把形狀直接寫出來。

## 檔案
| 程式 | 畫什麼 | 寫到哪裡 |
|---|---|---|
| `clay.py` | 共用的黏土畫法：一塊黏土 `clay()`、影子、亮光、手指印、搓出來的黏土條 `worm()`、眼睛、泡泡；形狀（圓、橢圓、圓角方形、平滑曲線）；存檔和裁到剛好 | （給其他程式用） |
| `customers.py` | 5 位客人（熊、兔、貓、豬、鴨）一般和開心兩種、`customers.json`；小朋友的廚師頭像 | `customers/`、`chef/` |
| `tools.py` | 廚房工具 20 樣、`anchors.json` | `tools/` |
| `food.py` | 食材和做好的食物 32 樣、`anchors.json` | `food/` |
| `ui.py` | 按鈕和小圖 12 樣、`anchors.json`；食譜書的 5 道菜 | `ui/`、`dishes/` |
| `scenes.py` | 3 張背景（1080×1920）、`scenes.json` | `scenes/` |
| `icon.py` | APP 圖示：戴廚師帽的小熊舉著煎蛋的小鍋子，蜜桃色背景 | Android、iOS 的圖示資料夾 |
| `preview.py` | 全部的圖排在一張大圖上（客人上面畫出嘴巴和頭頂的點） | 你指定的 PNG |
| `render_alpha.js` | 用 Chromium 把 SVG／HTML 畫成透明背景的 PNG（`preview.py`、`icon.py` 用） | |

## 怎麼跑
在這個資料夾裡，照這個順序（`food.py` 會用到 `tools.py` 的杯子和盤子，`ui.py` 會用到 `food.py`）：
```
python3 customers.py
python3 tools.py
python3 food.py
python3 ui.py
python3 scenes.py
python3 icon.py preview 圖示.png   # 圖示預覽：圓形、圓角方形、方形，48／96／192 像素，和一張大的
python3 icon.py export            # 寫進 Android 和 iOS
python3 preview.py 預覽.png        # 全部的圖排成一張，看看對不對（也可以只看幾類：python3 preview.py 預覽.png food ui）
```
畫 SVG 的程式只要 Python 3。`icon.py` 和 `preview.py` 還要 Pillow、Node.js 和 Playwright（Chromium）。

## 給 APP 用的說明
所有物件都裁到剛好，四周留 4 單位，背景透明。**站著的東西（側面看的）最下面就是圖的下緣**（影子也算在內，所以不用再往下留空）；從上面看的東西（盤子、砧板、鍋子……）四周都留 4。長的工具直直站著、用的那頭在下面（打蛋器、筷子、湯匙、湯勺）；刀子和平底鍋橫放（刀柄在左、鍋柄在右）。

下面 `anchors.json` 裡的點，數字都是那張 SVG 自己 viewBox 的單位（左上角是 0, 0）。

### 客人 `customers/`
- `<id>.svg`（笑著、眼睛張開）、`<id>_happy.svg`（眼睛 ^ ^、嘴巴張大、臉頰更紅）：大小和位置完全一樣，可以直接換。
- id：`bear`、`rabbit`、`cat`、`pig`、`duck`。
- 從腰以上，站在櫃台後面：**圖的下緣切平，就是櫃台的後緣**，兩隻手（翅膀）放在那條線上。每隻寬度都是 474，左右對稱（身體正中間在 x = 237），所有客人用同樣的比例畫，所以用同一個縮放比例放就一樣大。

`customers.json`，每位客人一筆：
```json
"bear": {
  "viewBox": {"width": 474, "height": 508},
  "mouth": {"x": 237.0, "y": 234.0},
  "mouthHappy": {"x": 237.0, "y": 231.3},
  "headTop": {"x": 237.0, "y": 8.2}
}
```
- `mouth`：一般表情的嘴巴中間（食物要送到的地方）；`mouthHappy`：開心表情張大的嘴巴中間。
- `headTop`：頭（含耳朵）最上面，點餐的對話框尾巴可以指到這裡上面一點。

### 廚師頭像 `chef/chef.svg`
小朋友的圓臉戴廚師帽，只有頭，正方形，放在圓形徽章裡。

### 背景 `scenes/`（1080×1920，不透明）
- `restaurant.svg`：暖色條紋牆、三角旗、兩盞吊燈、兩邊的架子（盤子、茶壺、罐子、盆栽），下面三分之一是櫃台；櫃台兩端有紙巾和服務鈴，中間空著。
- `kitchen.svg`：上面是磁磚牆（窗戶、罐子架、掛著的湯勺湯匙打蛋器），下面 60% 是木頭工作台（從上面一點點看），中間空著；後面兩個角落有小盆栽和鹽罐胡椒罐。
- `market.svg`（之後用）：傳統市場的菜攤，紅白遮雨棚、掛著的香蕉和蒜頭、桌上的蛋和秤，三箱高麗菜、番茄、紅蘿蔔（價格牌空白，APP 自己寫），下面是空的地面。
- 最上面 200 都很單純（放按鈕）。

`scenes.json`（y 都是在 1920 高度裡的位置）：
- `restaurant.counterBack` = 1280：櫃台後緣。**客人圖的下緣放在這條線上**，水平置中；寬度約畫面的 46% 看起來剛好。`counterTop` = 1330：櫃台檯面中間（放盤子）；`counterFront` = 1400：檯面前緣。
- `kitchen.worktopBack` = 814：工作台後緣（牆的影子下面）；`worktopMiddle` = 1340：工作台中間。
- `market.tableTop` = 960：攤子桌面；`cratesTop` = 1060：菜箱上緣；`ground` = 1330：地面開始。

### 工具 `tools/`
cutting_board、knife、bowl、bowl_egg、whisk、chopsticks、spoon、ladle、pan、pot、pot_boil、stove、sink、soap、plate、tray、cup、lid、straw、teapot。
- `bowl` 和 `bowl_egg` 一樣大；`pot` 和 `pot_boil` 一樣大（可以直接換）。
- `cup` 是透明塑膠杯（空的、半透明），`lid` 和 `straw` 照杯子的大小畫：蓋子的 `rim`（下緣中間）對到杯子的 `rim`（杯口中間）就剛好蓋上。
- `teapot`：側面、壺嘴朝左，倒茶時繞 `pivot` 轉，茶從 `spout` 流出來。

`tools/anchors.json` 的點：
- `cutting_board`：`center`、`area`（放食材的圓，`r` 是半徑）。
- `bowl`、`bowl_egg`、`plate`、`pan`：`center`、`inside`（裡面的圓和半徑：蛋汁、麵糊、食物放這裡）。
- `stove`：`center`、`flame`（火圈）。`pot`、`pot_boil`：`water`（水面中間）。`sink`：`spout`（水龍頭出水口）、`basin`（水槽中間）。`tray`：`center`。
- `cup`：`insideTopLeft`、`insideTopRight`、`insideBottomLeft`、`insideBottomRight`（杯子裡面的四個角，倒茶時把 `food/tea.svg` 裁在這個梯形裡往上長）、`rim`。`lid`：`rim`、`hole`。`straw`：`top`、`tip`（斜斜切開的下端）。
- `knife`：`tip`、`grip`。`whisk`：`loops`、`grip`。`chopsticks`：`tips`。`spoon`、`ladle`：`bowl`（湯匙裡面的圓）。`teapot`：`spout`、`pivot`。

### 食物 `food/`
tomato、tomato_slice、bread、cheese、sandwich、banana、banana_piece、strawberry、grape、skewer、fruit_skewer、egg、egg_half_left、egg_half_right、batter_raw、batter_cooked、crepe、danbing_roll、danbing_pieces、soy_paste、scallion、tea、milk、pearls、pearl、ice、milk_tea、wrapper、filling、wrapper_filled、dumpling、dumplings_plate。
- 一樣大、可以直接換的：`egg`、`egg_half_left`、`egg_half_right`（兩半放回原位就是一顆蛋，打蛋時往左右分開）；`batter_raw`、`batter_cooked`（同一個形狀，生的淡黃發亮、熟的金黃）；`wrapper`、`wrapper_filled`；`skewer`、`fruit_skewer`。
- `tea.svg`：100×200 的一塊茶（深琥珀色），上面是波浪；波浪每 100 重複一次，可以左右接起來。放在杯子後面、裁在杯子裡面往上升，就是倒茶。
- `scallion` 是幾小段蔥花（小），撒在蛋餅上。`filling` 大約一湯匙的肉餡，放在 `wrapper` 中間。
- `sandwich` 是早餐店的三角吐司，從切面看：吐司、起司、三片番茄、吐司。

`food/anchors.json`：
- `skewer`（和 `fruit_skewer` 一樣大）：`slot1`～`slot5` 是竹籤上五個水果的位置（由上到下：草莓、香蕉、葡萄、草莓、香蕉），`r` 是水果大約的半徑。小朋友一個一個串的時候，把 `strawberry`、`banana_piece`、`grape` 縮放到直徑約 2r 放在這些點上。
- `batter_raw`、`batter_cooked`、`crepe`、`wrapper`、`wrapper_filled`：`center`。

### 小圖 `ui/`
coin（金幣，上面沒有字）、star、recipe_book、check、hands_wash、adult_help（「請大人幫忙」的大人的手）、fire、heart、speech（空白的白色對話框，尾巴在下面）、arrow_flip（翻面的彎箭頭）、hand_hint（提示用的手指，指頭朝上）、sparkle。

`ui/anchors.json`：
- `speech`：`contentTopLeft`、`contentBottomRight`（框裡面放點餐內容的範圍）、`content`（中間）、`tail`（尾巴尖端）。
- `hand_hint`：`fingertip`（指尖，對準要點的地方）。

### 食譜書的菜 `dishes/`
sandwich、fruit_skewer、danbing、milk_tea、dumplings：做好、裝好盤的樣子，正方形。

### APP 圖示
`python3 icon.py export` 寫出：
- Android：`mipmap-{mdpi…xxxhdpi}/ic_launcher.png`（48～192，整張方形）；`mipmap-anydpi-v26/ic_launcher.xml` 加上 `drawable-{mdpi…xxxhdpi}/ic_launcher_foreground.png`、`ic_launcher_background.png`（108dp，小熊和鍋子都在中間 66dp 的安全圓裡）。`AndroidManifest.xml` 的 `android:icon` 是 `@mipmap/ic_launcher`。
- iOS：`AppIcon.appiconset/Contents.json` 列的每一張 PNG，照它的大小重畫，不透明。

## 改一張圖
1. 改對應的函式（例如 `food.py` 的 `strawberry_body`）。
2. 跑那支程式（如果別的程式也用到它，例如草莓也在水果串和食譜書裡，就照上面的順序都跑一次），再跑 `python3 preview.py 預覽.png` 看一下。
3. 要確定 flutter_svg 畫得出來：不要加濾鏡、遮罩、CSS；用 `clay.py` 的函式畫就沒問題。
