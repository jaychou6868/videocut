---
name: videocut
description: 短影片自動後製工作流（Remotion + ffmpeg）— 從原片+Hook素材到成品 MP4 的完整流程，包含 ~100 條實戰教訓。觸發情境：用戶說「剪影片」「做支新影片」「Hook 影片」「Remotion 模板」，或直接打 /videocut。
version: 1.0.0
argument-hint: [主題] [原片路徑] [Hook來源URL+秒數]
---

# Videocut — Remotion 短影片自動後製工作流

把長條教學原片 + 第三方 Hook 素材，自動剪成 IG Reels / TikTok / YouTube Shorts 格式（1080x1920 直式）的成品 MP4。

**這個 skill 是基於一支實際運作的 Remotion 模板系統（karen-video）累積的剪輯方法論**，包含手機安全區、渲染防抖、Hook 製作 SOP、特效極性規則、~100 條 debug 教訓。每支影片用同一個流程，但靠教訓避免重蹈覆轍。

## 前置需求（用戶必須有）

1. **Remotion 專案**（自己的 starter 或 fork karen-video 模板）
   - 必須包含：HookSection, FullVideo, AnimatedSubtitles, DynamicVideo, BrandBar
   - `OffthreadVideo` 不能用 `Video`（防渲染抖動，見 render-anti-jitter.md）
2. **ffmpeg + yt-dlp + whisper** 安裝在 PATH
3. **NLP / LLM API**（用於生成 Hook 文案 + CTA）— OpenAI / Claude / 自架皆可
4. **品牌資訊填寫**：在 Remotion 專案的 `video-config.ts` 設定品牌名、字體、品牌色、CTA 帳號

## 觸發詞（自動進入此 skill）

- 「剪影片」「做支新影片」「做新影片」「剪輯」「後製」「新的短影片」
- 「Hook 素材」「Remotion 模板」「影片模板」
- 用戶提到原片路徑 + Hook 連結 + 秒數
- 用戶輸入 `/videocut` 或 `/videocut <主題>`

## 啟動參數（argument）

- 無參數 → 互動問用戶：主題 / 原片路徑 / Hook 素材來源
- `/videocut <主題>` → 用主題當起點，問剩餘參數
- `/videocut <主題> <原片路徑> <Hook URL+秒數>` → 直接跑

## 8 步驟主流程（每步必過閘門）

```
□ 1. 素材就位
   ├── 原片（個人對鏡頭講話的長條 MP4）
   ├── Hook 來源（YouTube/TikTok/IG Reel URL + 起訖秒數）
   └── 主題（用主題對應 Hook 樣式 / variant 順序 / BGM mood，見 reference/topic-config.md）

□ 2. 轉錄
   ├── ffmpeg 提音頻 → whisper --model medium --language zh
   ├── LLM 校對術語（用戶領域的專業詞）
   └── 🔍 閘門 1：用戶確認 SRT（10 秒看一眼）

□ 3. 文案
   ├── NLP/LLM API 生成 Hook 銜接文案（痛點+好奇心缺口）
   ├── 生成兩版 CTA：LINE 版 + 留言版
   ├── 自動提取關鍵詞 → 高亮規則
   └── 🔍 閘門 2：用戶確認文案 + 高亮詞 + zoom 時刻

□ 4. 素材處理
   ├── yt-dlp 下載 Hook（指定段落）
   ├── ffmpeg 轉直式 1080x1920（blur-fill 背景）
   ├── ffmpeg 模糊 logo / 字幕帶 / 浮水印（見 hook-sop.md）
   ├── ffmpeg Jump Cut 主片（每句尾剪 100ms，最後一句不剪）
   └── ffmpeg 重新編碼修時間戳（防渲染抖動）

□ 5. 代碼
   ├── 填 Root.tsx 影片參數（SRT / 標題 / 高亮詞 / crackFrame）
   ├── selectZoomMoments() 自動計算 3-4 個 zoom 時刻
   ├── 建立兩個 Composition（`<Project>-LINE` / `<Project>-Comment`）
   └── 防抖確認：OffthreadVideo ✓ seededRandom ✓ 重編碼影片 ✓

□ 6. 安全區檢查
   └── 所有文字在頂部 200px ~ 底部 320px 之間，右邊距 180px（見 mobile-safe-zone.md）

□ 7. 預覽（不要直接渲染）
   ├── npx remotion studio src/index.ts --port 3333
   ├── 🔍 閘門 3：用戶在 Studio 看兩個 Composition 確認
   └── ⚠️ 等用戶說「OK 可以渲了」才進下一步

□ 8. 渲染 + 收尾
   ├── npx remotion render（兩版各一次）
   ├── 成品到用戶指定資料夾
   └── git tag vX.X
```

## 三大核心原則（不可違反）

1. **📱 手機安全區優先** — 影片是給手機用戶看的。頂部 0-180px 被 avatar 蓋、底部 1550-1920px 被用戶名/CTA 蓋、右側 900-1080px 被讚/留言/分享按鈕蓋。所有元素必須避開（詳見 `reference/mobile-safe-zone.md`）。

2. **🌐 網路調查優先** — 加新特效前必須去抖音/TikTok/Reels 找 3-5 支爆款（10 萬+），分析共同視覺元素再複刻。**不要憑空想像或自己設計**。原話：「你靠模仿自己去把它做出來，效果會非常非常爛」。

3. **🔇 少而有力** — 一支影片最多 2 個負面特效 + 2-3 個正面特效 + 2-3 個 emoji。節奏勝於花俏。動態 zoom 只用 3-4 個關鍵時刻，瞬間跳切（不漸變）。

## 必讀 reference 文件

執行此 skill 時，按下面順序讀進對應 reference：

| 階段 | 必讀文件 |
|------|---------|
| 開始前 | `reference/lessons.md` — ~100 條 debug 教訓總集 |
| 步驟 4 | `reference/hook-sop.md` — Hook 完整製作 SOP（下載 / 模糊 / 時間軸 / crackFrame） |
| 步驟 4 | `reference/ffmpeg-templates.md` — 所有 ffmpeg 指令模板 |
| 步驟 5-6 | `reference/render-anti-jitter.md` — 渲染防抖 6 條規則 |
| 步驟 6 | `reference/mobile-safe-zone.md` — 手機 UI 安全區規格 |
| 主題決策 | `reference/topic-config.md` — 主題對應 Hook 樣式 / variant / BGM 查閱表 |
| 文案生成 | `reference/nlp-prompts.md` — NLP/LLM prompt 模板（Hook / CTA / 標題） |

## 閘門紀律（最重要的反饋）

**每個 🔍 閘門必須停下等用戶明確確認**，不要連環跑到渲染。理由：

- **預覽階段改 1 字 = 免重跑** vs **渲染後改 1 字 = 重渲 30 分鐘 + 兩版 MP4 浪費**
- **絕對不要「我先渲好等等看」** — 等於浪費用戶時間和你的計算資源
- 在每個閘門明確說「請 review 確認後告訴我可以進下一步」

## 持續學習疊代

每支影片用戶反饋後：

- **單支影片問題** → 只改 Root.tsx 的 props（不動 config / SKILL.md / reference）
- **模板規則問題** → 改 video-config.ts + 對應 reference + 用戶的 memory
- **新踩坑** → 加進 `reference/lessons.md`，下次自動避開

**模板要越用越好，不是停留在當下狀態。**

## 個人化（其他人用此 skill 時要做的）

此 skill 從聲樂教學影片場景提煉，但流程通用。用戶要替換的部分：

1. **品牌資訊** — 在 Remotion `video-config.ts` 改品牌名 / 顏色 / CTA 帳號
2. **主題清單** — 在 `reference/topic-config.md` 加自己領域的主題（例：健身教練可改成 squat-form / pull-up / cardio 等）
3. **NLP API** — 在 `reference/nlp-prompts.md` 換成自己的 LLM 端點（OpenAI / Claude / 本地）
4. **聲樂專業詞校對** — 在轉錄階段的 LLM 校對 prompt 換成你的領域術語

## 相關專案模板

如果用戶沒有 Remotion 專案 starter，建議：

- 從 GitHub 找 Remotion 短影片模板 fork（搜尋 "remotion shorts template"）
- 或自己刻最小可用版本：HookSection + FullVideo + AnimatedSubtitles + DynamicVideo（OffthreadVideo）+ BrandBar

`reference/lessons.md` 涵蓋了所有踩過的坑，建議從零起步前先全讀。

## 給 Claude 的執行守則

1. **讀完 SKILL.md 後**先檢查用戶提供的參數，不齊就問
2. **每進入一個步驟前**讀對應 reference（按上方表格）
3. **每個 🔍 閘門必須停下** — 講「請確認後告訴我可以進下一步」，不要自動往下
4. **絕對不要直接 `npx remotion render`** — 先開 `npx remotion studio` 給用戶預覽
5. **發現新踩坑** → 寫進 `reference/lessons.md` 對應分類
6. 用戶反饋「視覺不夠強」「太花俏」「擋臉」「字太小」這類 → 對照 lessons.md 找出對應規則 + 修正
