# videocut — Claude Code Skill

短影片自動後製工作流（Remotion + ffmpeg）。從教學原片 + Hook 素材到成品 MP4 的完整流程，包含 ~100 條實戰教訓。

> 適用：聲樂教學、健身教練、料理達人、寫程式教學等任何「個人對鏡頭講話 + 第三方 Hook 素材」的短影片場景。

## 安裝

```bash
git clone <this-repo> ~/.claude/skills/videocut
```

或手動：

```bash
mkdir -p ~/.claude/skills/videocut
# 複製此 repo 全部內容（SKILL.md + reference/）進去
```

驗證安裝：在 Claude Code 對話中打 `/videocut`，應該會列出此 skill。

## 觸發方式

### 1. 直接打 slash command
```
/videocut                          # 互動式：問用戶主題、原片、Hook 素材
/videocut throat-strain            # 帶主題
/videocut throat-strain ~/Desktop/原片.mp4 https://youtu.be/abc?t=12
```

### 2. 自然語言觸發（Claude 自動進入）
- 「剪一支影片」「做支新影片」
- 「用 Remotion 模板做支關於 [主題] 的影片」
- 「我有原片 + Hook 素材想做短影片」

## 前置需求

1. **Remotion 專案**（自己的或 fork 一個 starter）
   - 必須包含：`HookSection`, `FullVideo`, `AnimatedSubtitles`, `DynamicVideo`, `BrandBar`
   - 必須用 `OffthreadVideo` 不能用 `Video`（防渲染抖動）
   - 推薦結構參考 `reference/topic-config.md`

2. **CLI 工具**
   - `ffmpeg` — 影片處理（必裝）
   - `yt-dlp` — 下載 YouTube/IG/抖音 Hook 素材
   - `whisper` — 自動轉錄（推薦 medium 模型）

3. **LLM API**（生成 Hook 文案 + CTA）
   - OpenAI / Claude / 自架皆可
   - prompt 模板在 `reference/nlp-prompts.md`

4. **品牌資訊**（在 Remotion 專案 `video-config.ts` 設定）
   - 品牌名 / 字體 / 品牌色 / CTA 帳號 / LINE handle

## 結構

```
~/.claude/skills/videocut/
├── SKILL.md                          # 主入口（Claude 載入這份做流程導航）
├── README.md                         # 本檔（給用戶看的安裝/說明）
└── reference/
    ├── lessons.md                    # ~100 條 debug 教訓總集
    ├── render-anti-jitter.md         # 渲染防抖 6 條規則
    ├── hook-sop.md                   # Hook 完整製作 SOP
    ├── ffmpeg-templates.md           # 所有 ffmpeg 指令模板
    ├── mobile-safe-zone.md           # 手機 UI 安全區規格
    ├── topic-config.md               # 主題對應 Hook/variant/BGM 查閱表
    └── nlp-prompts.md                # LLM prompt 模板
```

## 8 步驟主流程

```
1. 素材就位 → 主題 / 原片 / Hook URL
2. 轉錄 → whisper SRT → 🔍 用戶確認
3. 文案 → LLM 生成 Hook 銜接 + 兩版 CTA → 🔍 用戶確認
4. 素材處理 → yt-dlp / 直式轉換 / logo 模糊 / Jump Cut / 重編碼
5. 代碼 → 填 Root.tsx 參數 + 兩個 Composition
6. 安全區檢查 → 所有元素避開頂部/底部/右側 UI
7. 預覽 → npx remotion studio → 🔍 用戶確認（必過閘門）
8. 渲染 → 兩版 MP4 → 收尾
```

## 三大核心原則

1. **📱 手機安全區優先** — 影片給手機用戶看，平台 UI 會蓋邊緣
2. **🌐 網路調查優先** — 加新特效前找抖音/TikTok 爆款 3-5 支分析
3. **🔇 少而有力** — 一支影片最多 2 個負面 + 2-3 個正面 + 2-3 emoji

## 個人化（用其他領域）

Skill 從聲樂教學影片提煉，但流程通用。換領域要做：

| 替換項目 | 範例（聲樂 → 健身）|
|---------|-------------------|
| 主題清單（`reference/topic-config.md`）| throat-strain → squat-form-fail |
| LLM 校對術語 | 副歌/胸聲 → squat/deadlift |
| 失控詞 | 走音/破音 → 腰垮/動作崩 |
| BGM mood | ambient/soft-piano → gym-energetic/rock |
| 品牌資訊 | @thisissingple → 你的 LINE handle |

詳見 `reference/topic-config.md` 的「換領域使用此 skill」章節。

## 為什麼是這個流程

這個 skill 不是「教 Claude 怎麼用 Remotion」— 那是 Remotion 官方文件的事。  
這個 skill 是「累積一支真實運作的 Remotion 短影片系統的 ~100 條踩坑紀錄」。

每條 lesson 都來自實際做影片時的 debug：
- 「為什麼預覽正常但渲染人頭一直抖？」→ `<Video>` vs `<OffthreadVideo>`
- 「為什麼字幕擋臉？」→ 手機安全區規則
- 「為什麼用戶反饋『最後一句沒講完』？」→ SRT lastEnd 對齊 mp4 duration
- 「為什麼負面特效用紅 badge 看起來突兀？」→ 灰階本身就是強訊號
- 「為什麼 Hook 跟主片邏輯跳？」→ Hook countdownCta 當「銜接橋」

照流程走 = 自動避開這些坑。

## 持續疊代

每用此 skill 做完一支影片：
- 用戶反饋 → 加進 `reference/lessons.md` 對應分類
- 模板規則演進 → 改 `reference/topic-config.md`
- 模板要越用越好，不是停留在當下狀態

## 來源

從 Karen（簡單歌唱訓練師）的 Remotion 影片後製系統 `karen-video` v1.9 提煉而成（2026-04-13 初版 → 2026-04-25 v1.9，已生產 6 支影片）。

## License

MIT — 拿去用、改、分享都歡迎。如果這份 skill 幫你省時間，引用 ~~karen-video 專案~~ 或 fork 後 star 一下。
