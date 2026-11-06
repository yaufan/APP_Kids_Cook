# 給 Claude 的專案規則（動物小餐廳）

這份是這個專案的「記憶」。每個在這個專案裡工作的 Claude 都要照著做。它是「畫畫小鎮」（https://github.com/yaufan/APP_Kids_Paint）和「字母寵物」（https://github.com/yaufan/APP_Kids_Paint_for_learning_writing）的兄弟 APP，技術和流程照那邊（畫風不同），這裡寫這個專案自己的事。程式的架構最接近字母寵物，有疑問先看那邊怎麼做。

## 和使用者合作
- **一律用繁體中文回覆**，用白話說明，少用技術名詞；要用的話順便解釋。
- 使用者用手機上的 Claude App 看對話，**打不開 artifact 連結**。圖片、影片、聲音、QR code 都用傳檔案的方式（SendUserFile）給。
- 設計階段：每個想法都畫成草圖（`docs/mockups/`）傳給使用者看，再問。
- 之後每做完一版：給示範影片片段、手機截圖、下載 QR code（和畫畫小鎮一樣）。
- 有要使用者決定的事，列出選項和我的建議，再問。
- 不要開 pull request，除非使用者要求。用了網路搜尋，回覆最後附「Sources:」和連結。

## 這個 APP
- 給 3～6 歲的小朋友，在台灣，國語為主：開一間動物餐廳，照圖片食譜做菜給動物客人吃。
- 每個做菜動作是一個小遊戲；玩的時候學數數、顏色形狀、做事的順序、均衡飲食（國民健康署「我的餐盤」）、廚房安全和台灣的食物。
- 設計在 [docs/design.md](docs/design.md)，改設計時一起改它。
- 不連網、不定位、沒有廣告、沒有帳號。以後上架要收費：免費下載、一次買斷完整版，購買只在家長模式（要過家長關卡）。
- 畫風：**黏土風**（圓胖、柔和的立體感、沒有框線），和畫畫小鎮的粗框貼紙、字母寵物的水彩繪本都**要不一樣**。
- 不會失敗、不催促、沒有倒數扣分；金幣只能做菜得到，只能換裝飾。
- 每個動作都要有音效，每位客人有自己的聲音；音樂分餐廳、做菜、食譜書。
- 授權：非商業使用（`LICENSE`），中英文版本；別人做的部分（字型）在 `NOTICE.md`。專案目前公開。
- 名稱：動物小餐廳。

## GitHub Actions
- 工作流程（照字母寵物；第一次放上 main 前要先問）：
  - `app.yml`（App）：推到 `main` 而且改到 `app/**` 時跑分析、全部測試（含完整流程）、打包 APK，約 15～20 分鐘。
  - `release.yml`（Release）：推到 `main` 而且改到 `app/pubspec.yaml`、`CHANGELOG.md` 或它自己時，版本還沒發布過就打包三個 APK 放上 Releases，約 20 分鐘；版本沒變約 1 分鐘。
  - `cleanup.yml`：手動，刪舊的建置檔案，約 1 分鐘。
- 推工作分支（`claude/...`）不會啟動任何工作流程。
- 簽章：和畫畫小鎮用**同一把測試金鑰**（別名 `kidspaint`），Secrets 名稱一樣：`ANDROID_KEYSTORE_BASE64`、`ANDROID_KEYSTORE_PASSWORD`，要放在這個專案的 Actions → Secrets → Repository secrets。指紋 `TEST_KEY_SHA256` 寫在工作流程裡。以後上架要換成正式的上傳金鑰。
- 發新版本：`app/pubspec.yaml` 的 `version`、`app/lib/app/version.dart` 的預設值、`CHANGELOG.md` 最上面一段（`## 版本 …`）三個要一致（`test/version_test.dart` 檢查）。
- **任何會啟動 Actions 的動作，都要先問使用者，等使用者同意才做**，問的時候說清楚四件事：
  1. 會跑哪些工作流程。
  2. 這次大約用掉幾分鐘。
  3. 這個月目前用了多少。
  4. 跑完大約還剩多少。

  規則和畫畫小鎮的 `CLAUDE.md` 一樣；那個帳號每月 2,000 分鐘是所有私有專案共用的，Mac 主機的 1 分鐘算 10 分鐘。

## Git
- **發布新版本、做成可以安裝的 APK、給下載 QR code**：照 skill `release-kids-app`（`.claude/skills/release-kids-app/SKILL.md`），七個兄弟 APP 共用同一份；新 APP 開始時把這個資料夾複製過去。
- 在系統指定的 `claude/...` 工作分支上開發，commit 完就推這個分支。
- commit 訊息用英文寫清楚改了什麼和為什麼，結尾加系統要求的署名行。不要寫模型名稱。
- 不能 commit：金鑰、密碼、不公開的文件。

## 和畫畫小鎮共用的做法（開始寫程式時照著做）
- Flutter 3.47.8、Riverpod、flutter_svg、audioplayers、flutter_tts。存檔是一個 JSON 檔（`app/lib/core/store.dart`），沒有用 drift，所以本機跑測試**不用** sqlite 那段，直接 `flutter test`。
- 觸控：用原始的手指事件（`Listener`），手指一碰就畫。不要用拖曳手勢，它要移動 36 點才開始，小朋友短短的一筆會不見。
- 圖和聲音都用程式產生（SVG 用 Python 畫；聲音用 numpy 合成），不用別人的素材。
- 本機測試：在 `app/` 裡 `flutter test`（不含 `test/flow_test.dart`），`flutter analyze` 要零問題。以後加了 drift，才照畫畫小鎮的 `tools/run_tests.sh`（pubspec 的 sqlite 那段不能 commit）。
- 完整流程和截圖：`flutter test test/flow_test.dart`，截圖在 `app/build/screenshots/`。
- 示範影片（每一版都要給使用者）：在 `app/` 裡 `flutter test test/demo/demo_video_test.dart --dart-define=DEMO=true`（約 5～10 分鐘，要 ffmpeg），再在專案根目錄 `python3 tools/demo_audio.py` 把背景音樂和音效混進去。輸出 `app/build/demo/demo.mp4`；`chapters.txt` 是每一段開始的格數（每秒 10 格），用來剪新功能的片段。

## 程式在哪裡
- `app/lib/core/`：菜和步驟（`dishes.dart`）、遊戲的存檔和規則（`game.dart`）、存檔、聲音、語音。
- `app/lib/features/`：餐廳（`restaurant`）、廚房和每一步的小遊戲（`kitchen`）、食譜書（`book`）、家長關卡和家長模式（`parent`）。
- 圖：`design/art/`（Python 畫 SVG，黏土風）；聲音：`design/sounds/make_sounds.py`。
