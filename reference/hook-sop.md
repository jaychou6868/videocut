# Hook 完整製作 SOP

從第三方影片素材到處理乾淨可用的 Hook 段。

---

## 1. 素材選擇原則

### 1.1 來源
- YouTube / Bilibili / Vimeo（用 yt-dlp）
- IG Reel（yt-dlp 直接支援）
- 抖音（2026-04 後反爬，需 Chrome MCP — 詳見 `ffmpeg-templates.md` ②）
- TikTok（用 yt-dlp 或第三方下載器）

### 1.2 內容篩選
- 必須有強烈情緒峰值（破音 / 走音 / 失控 / 高潮 belt 等）
- 避開有明顯版權保護的官方 MV（用片段 + 模糊 logo 處理灰色地帶）
- 影片長度足夠：6-10 秒可剪，原片至少要有完整一段情緒（不要只剪走音瞬間）

### 1.3 主題對應
查 `topic-config.md` 找對應主題的 Hook 樣式 / variant 順序 / BGM mood。

### 1.4 表演者驗證（重要）
- 用戶提供的表演者名字可能跟原片實際不符（記憶 mismatch）
- 下載後讀 Chrome tab title + 抽 4 frames @ 1.5/5/8/11s 確認 boundary
- 不符回問用戶

### 1.5 檔名只當 hint
- Desktop 檔名「喉嚨緊繃酸痛.mp4」可能 SRT 出來其實是「共鳴／聲音薄飄」
- 必須等 Whisper 出 SRT 後才確認主題
- 檔名只是 hint，以實際內容為準

---

## 2. 下載流程

### 2.1 YouTube 指定段落
```bash
yt-dlp -f "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best" \
  --download-sections "*開始秒-結束秒" \
  -o hook_raw.mp4 \
  "YouTube_URL"
```

### 2.2 IG Reel（不需指定段落，整支下載）
```bash
yt-dlp -f "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best" \
  -o hook_full.mp4 \
  "https://www.instagram.com/reel/<id>/"
```

### 2.3 抖音（Chrome MCP 流程）
1. 用 Chrome MCP 開抖音真實 URL
2. `read_network_requests` 抓 mime_type=video_mp4 的 `*.douyinvod.com` URL
3. `curl -L -H "Referer: https://www.douyin.com/" -H "User-Agent: <Chrome UA>" -o hook_raw.mp4 "<URL>"`
4. 1 小時內完成（URL 有時效）

---

## 3. Hook 片段剪切原則（情感完整 > 時長精簡）

### 3.1 完整情緒
- **不要**只剪走音/破音瞬間
- **要**讓人物把整句話/反應說完
- 範例：走音在 7s → 不剪 5-10s，剪 4-12s 含完整「你們不會跑掉嗎我就問」反應

### 3.2 Duration 靈活
- 6-10 秒視內容調整
- 不固定 6 秒
- 用戶反饋「Hook 4-10s 太生硬，切在說話中途」

### 3.3 Hook boundary 用視覺幀確認
Whisper 對 live + 多人合唱 + 伴奏識別不準。改用視覺：
```bash
ffmpeg -i hook.mp4 -vf "fps=2" frames_%03d.jpg
```
抽 14 張幀（每 0.5s 一張）找 climax 動作最強那一幀。

**範例 climax 訊號：**
- 雙手高舉 + 嘴張開直視鏡頭 = belt 巔峰
- 臉部肌肉繃緊 + 眼神失焦 = 破音瞬間
- 表情失守（笑/驚 frozen frame）= 反應峰值

---

## 4. 直式轉換（橫式 → 1080x1920 blur-fill）

```bash
ffmpeg -ss 起始 -t 時長 -i hook_raw.mp4 \
  -filter_complex "\
    [0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=25:5[bg]; \
    [0:v]scale=1080:-2[fg]; \
    [bg][fg]overlay=(W-w)/2:(H-h)/2[out]" \
  -map "[out]" -map 0:a \
  -c:v libx264 -preset medium -crf 20 -c:a aac -b:a 128k hook.mp4
```

**IG Reel 例外：** 已是 1080x1920 直式 → 跳過此步驟。

---

## 5. Logo 模糊（防版權，雙層 gblur）

### 5.1 找 logo 精確座標
```bash
ffmpeg -i hook.mp4 -vf "select=eq(n\,60),crop=350:120:0:710" \
  -vsync vfr -q:v 2 /tmp/logo_check.jpg
```
反覆調整 `crop=W:H:X:Y` 直到精確框住 logo。

### 5.2 雙層模糊
```bash
ffmpeg -y -i hook.mp4 -filter_complex "
  [0:v]split=3[main][c1][c2];
  [c1]crop=W:H:X:Y,gblur=sigma=80[b1];
  [c2]crop=W:H:X:Y,gblur=sigma=40[b2];
  [main][b1]overlay=X:Y[t1];
  [t1][b2]overlay=X:Y[out]
" -map "[out]" -map 0:a -c:v libx264 -crf 20 -c:a copy hook_clean.mp4
```

### 5.3 關鍵規則
- logo 區域寬度 ≥ 實際文字寬度 + 150px buffer
- 雙層 gblur（80 + 40）— 不單層 sigma=50（會留可讀殘影）
- 殘影測試：放大成品看，文字邊緣應完全消失

### 5.4 錯誤方法（不要做）
- ❌ CSS backdrop-filter — 位置對不準
- ❌ drawbox 黑色方塊 — 醜，蓋臉
- ❌ Remotion 漸層遮蓋 — 位置不精確
- ✅ 唯一可靠：ffmpeg crop+gblur+overlay 精準座標

---

## 6. Hook 原片字幕帶遮擋（整條 vs 分塊）

### 6.1 整條全寬遮（人物在中央偏上時）
```bash
# y:950-1060 整條 1080 全寬模糊
ffmpeg -y -i hook.mp4 -filter_complex "
  [0:v]split=2[main][c1];
  [c1]crop=1080:110:0:950,gblur=sigma=60,gblur=sigma=30[b1];
  [main][b1]overlay=0:950[out]
" -map "[out]" -map 0:a -c:v libx264 -crf 20 -c:a copy hook_clean.mp4
```

**為什麼整條遮：** 字幕會隨時間換句，1 幀 leak 觀眾就看到。

### 6.2 分塊小區域（人物身體在中央時）
整條全寬會遮腰部 → 改分 3 塊（左下/右上/右下）剛好遮文字 + 小 buffer：
```bash
ffmpeg -y -i hook.mp4 -filter_complex "
  [0:v]split=4[main][c1][c2][c3];
  [c1]crop=340:90:740:0,gblur=sigma=60,gblur=sigma=30[b1];     # 右上 logo
  [c2]crop=270:160:0:1640,gblur=sigma=60,gblur=sigma=30[b2];   # 左下燒字
  [c3]crop=250:90:830:1830,gblur=sigma=60,gblur=sigma=30[b3];  # 右下廣告
  [main][b1]overlay=740:0[t1];
  [t1][b2]overlay=0:1640[t2];
  [t2][b3]overlay=830:1830[out]
" -map "[out]" -map 0:a -c:v libx264 -crf 20 -c:a copy hook_clean.mp4
```

雙層 gblur sigma=60+30 即可（不需要 80+40 / 100+50 那麼強）。

---

## 7. IG/媒體源頭頂部燒字 + 底部水印

情境：IG Reel / 微博 / 抖音轉發類媒體頻道。畫面結構：
1. 頂部燒字（黃底+白底兩行新聞標題）+ 頻道 logo
2. 中央飄字（後製加的擾動字）
3. 底部水印（「來源: XXX / 如有侵權請聯絡刪除」）

### 7.1 遮罩策略
| 區域 | 處理 | 原因 |
|------|------|------|
| 頂部燒字 + logo | **遮掉**（疊自家 NLP-生 headline）| 自家標題要露臉 + 跟主片邏輯橋銜接 |
| **中央飄字** | **保留** | 增加「媒體後製」對照感（網民批評歌手 → 我們點出真因），不擋臉、不違和 |
| 底部水印 | 遮掉 | 隱藏源頭、避免觀眾追溯 |

### 7.2 ffmpeg 範例
```bash
ffmpeg -y -ss <start> -t <duration> -i hook_full.mp4 -filter_complex "
  [0:v]split=3[main][c1][c2];
  [c1]crop=1080:380:0:0,gblur=sigma=80,gblur=sigma=40[b1];
  [c2]crop=1080:240:0:1680,gblur=sigma=60,gblur=sigma=30[b2];
  [main][b1]overlay=0:0[t1];
  [t1][b2]overlay=0:1680[out]
" -map "[out]" -map 0:a \
  -af "afade=t=out:st=<dur-0.4>:d=0.4" \
  -c:v libx264 -preset medium -crf 20 -c:a aac hook_clean.mp4
```

### 7.3 重要：頂部範圍 y=0-380（不是 y=0-300）
- 頻道 logo 通常在 y=265-330
- y=0-300 漏掉 logo 一部分
- y=0-380 = 兩行燒字 + logo + 50px buffer
- 一次到位避免 logo 殘留

---

## 8. Hook 文字時間軸 SOP

Hook 段每個文字元素的出場順序和對齊規則：

| 時間 | 元素 | 動作 |
|------|------|------|
| **0-1.5s** | headline + subheadline | 淡入（兩行新聞風格，top=200/280）|
| **1.5s – crack** | 只顯示原片畫面 | **不疊中央大字**（讓人物情緒主導畫面）|
| **crackFrame + 0.5s** | bigText2 警告樣式入場 | 紅底金邊 + ⚠⚠ + 抖動 + 脈動紅光（`bigText2Entry = crackFrame + 15`）|
| **同時** | ShatterEffect + MangaText | 用 whisper word-level timestamp，對齊到「歌手唱出關鍵字」的**那一幀**（不是句首，是 word onset）|
| **copyLeadSeconds 之前** | top 文字淡出 | `topFadeOutStart = copyStart - 0.5s` |
| **最後 copyLeadSeconds 秒** | 底部 copy + 倒數 | 痛點 question + CTA hook + 倒數 3→2→1 |
| **最後 18 幀** | 全體 exit fade | `exitOpacity` 統一淡出避免斷崖 |

---

## 9. crackFrame 對齊（whisper word-level timestamp）

### 9.1 用 word-level timestamp
```bash
whisper hook_audio.wav --model medium --language zh --word_timestamps True
```

### 9.2 找關鍵字 onset
- 主題對應的關鍵字（throat-strain → 「害怕」「疼」「撐不住」/ high-notes → 「破音」「卡」/ pitch-accuracy → 走音那個音）
- 拿到 word onset 秒數
- 30fps 下 crackFrame = onset_s × 30

### 9.3 範例
- 主題：throat-strain
- whisper 分析「怕」word onset 落在 3.74s
- 30fps 下 crackFrame = 112（≈3.73s）
- 結果：manga「害怕」剛好在歌手 belt 到「怕」音峰時 pop 出來，視聽同步

### 9.4 例外：live + 多人合唱用視覺幀
Whisper 對伴奏 + 和聲識別不準。改用視覺：
- 抽密集幀（fps=2）找 belt 動作最強那一幀
- 用幀號 ÷ fps = onset 秒數
- crackFrame = onset_s × 30

---

## 10. crackFrame 禁用規則

當主題不需要中央大字 / shatter / manga 時：

```typescript
// Root.tsx 設定
const hookContent = {
  // ...
  bigText: "",
  bigText2: "",
  mangaText: "",
  reactionText: "",
  crackFrame: 9999,  // 任何 > hookDurationFrames 的值
};
```

**何時禁用：**
- 原片已有強烈燒字中央大字（如burnt-in「破音」「唱不上去」紅字）
- 心理類主題（confidence-stage, emotion-expression）
- 主題不適合 shatter/manga/reaction 效果

**自動 disable：** HookSection 內建 `crackEffectsActive` flag 偵測 `rawCrackFrame >= durationInFrames` → 自動禁用 ShatterEffect + 音效 + bigText2 opacity interpolate（不用另外改代碼）。

---

## 11. Hook 跟主題不匹配時的 SOP

有時候用戶拿到的 Hook 素材跟主題概念不完全對應（例：張學友破音片段 → 不敢開口主題）。

### 11.1 處理流程
1. **先 flag 不匹配**，讓用戶決定 (A) 換素材 (B) 換主題 (C) 硬剪加文字銜接
2. 如果選 (C)，**原片燒字當權威對照組**：不要完全遮掉，保留強烈視覺元素當「連大咖都 X / 何況你」的對照
3. **NLP 生底部銜接文案做語意橋接**，把燒字內容 → 主片主題串起來
4. **Hook 最後 0.4s 做軟轉場**：ffmpeg `afade=t=out:st=5.4:d=0.4` 音頻淡出 + HookSection `exitOpacity` fade to black，避免硬切斷
5. **頂部標題要押韻主片關鍵句**（例：副標「難怪你不敢開口」→ 主片第 6 句「真正擋住你的」）

### 11.2 心理類主題不用警示樣式
- 上台緊張 / 不敢開口 / 沒感情等心理類主題，**不**用 warning-red-gold（紅底金邊 + ⚠⚠）
- 改用「無中央大字」+ 原片燒字當權威對照組 + 自家 NLP-生 headline 在頂部 + soft-piano BGM
- crackFrame=9999 禁用

**原因：** 心理恐懼類走共鳴而非警示，警示讓觀眾覺得「被指責」→ 划走率升高。喉嚨酸痛＝生理警訊適合警示；不敢開口＝情緒脆弱需要共鳴。

---

## 12. Hook 主標 + 副標寫作 SOP

### 12.1 第一行黃底黑字（13-18 字）
範本：人物 + 動作 + 節目  
範例：「前港姐陳凱琳登《乘風2026》」

### 12.2 第二行白底黑字（10-15 字）
範本：動詞 + 具體缺點 + 加號或 emoji  
範例：「唱歌遭批魔音貫耳＋overact」

### 12.3 用戶偏好
- 「新聞八卦向」優先（避「淚水堅毅」「感情詮釋如何更自然」這種文藝/詩感）
- 動詞用「翻車」「遭批」「斷線」「全亂」
- 用「翻車」OK，避「大咖」「真相」「教幾招」（用詞限制看用戶領域）

### 12.4 押韻主片關鍵句
頂部副標必須押韻主片關鍵句（例：副標「難怪你不敢開口」→ 主片第 6 句「真正擋住你的」）。

---

## 13. Hook ↔ Main 邏輯銜接橋

觀眾從 Hook 失控 → 主片直接講解法，邏輯會跳。Hook countdownCta 當「銜接橋」：

1. **揭三大失控的根因**（例：「身體用錯位置」）
2. **承諾「現在搞懂立刻改變」**
3. → 主片頂部 line 1 加生活化前綴接觀眾日常（「唱歌、飆高音卡死？」）
4. → line 2 點主片真因（「問題根本不在喉嚨」）
5. → line 3 後果（「拖久了講話也回不來」）

**整條邏輯：** Hook 失控 → 真因（CTA 揭露）→ 主片 line 1 對齊觀眾經驗 → line 2 鎖真因 → line 3 鎖後果。
