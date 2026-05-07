# Lessons Learned — 短影片後製通用教訓

從多支實戰累積的踩坑紀錄。每條都有「規則」+「原因」+「How to apply」。

---

## 📐 字幕 / 文字

### 1. 不要花俏動畫
**規則：** 字幕**不**用波浪、霓虹、火焰、旋轉等動畫。  
**原因：** 「有點醜」— 用戶反饋。專業感和可讀性比花俏重要。  
**正解：** 排版做到好看 — 粗描邊 + 關鍵詞放大變色 + pop 入場然後**靜止**。

### 2. 字體寧大勿小
**規則：** 字幕至少 58px，標題至少 56px+，品牌至少 68px。  
**原因：** 用戶反饋「太小」N 次。手機螢幕在強光下小字看不清。  
**Hook 倒數區規格：**
- 痛點提問：58px 粗體 白色
- 解法預告：46px 金色
- 倒數數字：72px 粗體 金色發光

### 3. 字體只用一種家族（NotoSansTC 或對應語言）
**規則：** 不混用 DancingScript / KleeOne 等多家族字體。  
**原因：** Google Font 載入超時 → 整個畫面變透明格子。  
**例外：** emoji 是 Apple Color Emoji 字體，OK；Logo/品牌可用設計過的圖檔。

### 4. 同行字體大小一致
**規則：** 同一行除了高亮詞外，字體大小一致。  
**原因：** CTA 行用 highlight rule 導致部分字放大 → 視覺混亂。

### 5. 金色閃光用 text-shadow，不要 background-clip
**規則：** 用 `text-shadow` 脈動光暈做金色閃光。  
**原因：** `WebkitBackgroundClip: "text"` 在 Remotion 渲染會變成一塊金條。

### 6. CTA 兩行同時顯示，不分先後
**規則：** CTA 兩行同畫面 spring-pop 一次進場，停留到最後一幀。  
**原因：** 一句一句跳出觀眾來不及讀。

### 7. CtaOverlay defaultProps 不能塞 JSX
**規則：** Remotion `Composition.defaultProps` 必須 JSON serializable。重點字染色用 `string + highlights: ["位置", "LINE"]` 模式，不要塞 React Element。  
**原因：** React element object 不能 serialize，會噴 "Objects are not valid as a React child"。  
**正解：** Component 內部 `escapeRegExp + split + map` render `<span style={{color}}>` 染色。

---

## 🎬 動態效果

### 8. Zoom 只用 3-4 個關鍵時刻
**規則：** 動態 zoom 不要每句都做。  
**原因：** 視覺疲勞，用戶反饋「動態縮放又有點過多了」。

### 9. Zoom 必須瞬間跳切，不漸變
**規則：** 不用 spring 過渡，直接切換。  
**原因：** 漸變看起來軟，瞬間切換有衝擊感。  
**參數：** zoom 倍率 1.15x，transformOrigin "50% 35%"（朝臉部）。

### 10. Emoji 最多 2-3 個
**規則：** 一支影片 emoji 不超過 3 個出場時刻。  
**原因：** 太多 emoji 看起來廉價。  
**比例參考：** ~18%（5 emoji on 28 lines），不要太滿。

### 11. emoji 字級 82px（不是 64）
**規則：** `CONFIG.accent.emojiFontSize` = 82px。  
**原因：** 64px 用戶反饋「emoji 看起來有點小」。

### 12. 不要自己從零寫動畫
**規則：** 加新效果前先找現成模板/套件。  
**原因：** 自己寫的動畫沒有爆款研究 → 效果差、又花時間。  
**參考：** 抖音/TikTok/Reels 爆款 → 截圖存 reference/viral-samples/ → 分析共同元素 → 複刻。

---

## 🛠 技術陷阱

### 13. Jump Cut 用 ffmpeg 預剪，不用 Remotion Series
**規則：** Jump Cut 必須用 ffmpeg `filter_complex` 預剪成單一影片。  
**原因：** Remotion `<Series>` 切片段會產生黑幀閃爍。

### 14. 最外層 AbsoluteFill 必須加 `backgroundColor: "black"`
**規則：** 永遠帶黑底。  
**原因：** 否則轉場時露出透明格子。

### 15. const 變數要在使用前宣告
**規則：** `crackFrame` 等 const 必須在 use 之前宣告。  
**原因：** JavaScript const 沒有 hoisting，會 ReferenceError 白屏。

### 16. 不要為了修抖動刪減效果
**規則：** 抖動問題在底層組件（Video vs OffthreadVideo），不在效果本身。  
**原因：** 應修根因，刪效果只會降低成品品質。詳見 `render-anti-jitter.md`。

### 17. Remotion bundle cache 大坑
**規則：** 新加 `public/` 資產後若報 404，清 webpack cache。  
**指令：** `rm -rf /var/folders/*/remotion-webpack-bundle-*` + 渲染加 `--public-dir=<abs>`。  
**原因：** Cached bundle 不重 bundle，新加的素材找不到。

### 18. crackFrame 禁用要用 9999 + guard
**規則：** 主題不需要中央大字 / shatter / manga 時，把 `bigText/bigText2/mangaText/reactionText = ""` + `crackFrame = 9999`。  
**原因：** crackFrame 設成 > durationInFrames 的值會讓 HookSection 自動 disable shatter + 音效 + interpolate。  
**Guard 內建：** HookSection 的 `crackEffectsActive` flag 偵測 `rawCrackFrame >= durationInFrames` 自動禁用，不用另外改代碼。

---

## 📝 內容 / 文案

### 19. 文案用 NLP/LLM 生成，不要自己編
**規則：** Hook 銜接 + CTA 都用 API 生成。  
**原因：** 自己編的文案缺少心理學模式，缺乏停留與行動驅動。  
**詳見：** `nlp-prompts.md`

### 20. Hook 完整情緒 > 時長精簡
**規則：** Hook 不要只剪走音/破音那瞬間，要包含完整前後情緒。  
**範例：** 走音在 7s → 不是剪 5-10s，而是剪 4-12s（含人物說完反應句）。  
**Duration：** 6-10 秒視內容調整，不固定 6 秒。

### 21. Hook 跟主片要押韻 / 邏輯銜接
**規則：** Hook 頂部標題押韻主片關鍵句；Hook 底部 CTA 揭真因 + 承諾改變 → 主片頂部 line 1 用生活化前綴接上 → line 2 點真因 → line 3 點後果。  
**範例：** Hook 底部「身體用錯位置, 現在搞懂, 立刻改變 👇」→ 主片 line 1「唱歌、飆高音卡死？」line 2「問題根本不在喉嚨」line 3「拖久了講話也回不來」。

### 22. 主片頂部 line 1 加生活化前綴
**規則：** 不要寫太硬的提問（「飆高音脖子卡死？」），加日常情境前綴（「唱歌、飆高音卡死？」）。  
**原因：** 太硬的提問跟 Hook 失控場景沒銜接 → 觀眾覺得跳。  
**情境 hint：** KTV / 朋友面前 / 慶生 / 聚餐 / 日常。

### 23. Hook 文案不要 frame 主片答案
**規則：** Hook 描述失控狀態（咬字糊+音準歪+節奏亂），不要寫主片才揭露的詞（聲帶硬扛/聲帶緊繃/真相）。  
**原因：** 過早 frame 答案 = 觀眾沒動力看主片。

### 24. bigText2 不用「警報！」開頭
**規則：** warning-red-gold 樣式本身已 ⚠⚠ + 紅底金邊脈動，不用文字再強調「警報」。  
**正解：** 直接寫描述狀態句（「節奏全亂!看傻觀眾」）。

### 25. CTA 兩版領取統一
**規則：** LINE 版 + 留言版的「秘笈名稱」line 必須統一（例：「高音錯誤修正秘笈」）。  
**原因：** funnel 不一致觀眾困惑。  
**差異點：** 只有 line1 行動指令不同（「加入官方LINE」vs「留言關鍵字」）。

### 26. CTA 重點字染色標出來
**規則：** CTA 觀眾要記憶的關鍵 keyword 染色（紅 #FF6B6B），不要全白。  
**範例：** LINE 版重點：「LINE」+「秘笈名稱」/ 留言版重點：「位置」+「秘笈名稱」。

---

## 🎭 心理 vs 警示主題

### 27. 心理類主題不用警示樣式
**規則：** 上台緊張 / 不敢開口 / 沒感情等心理類主題，**不**用 warning-red-gold（紅底金邊 + ⚠⚠）。  
**原因：** 爆款研究結論：心理恐懼類走共鳴而非警示，警示讓觀眾覺得「被指責」→ 划走率升高。  
**正解：** 心理類用「無中央大字」+ 原片燒字當權威對照組 + 自家 NLP-生 headline 在頂部 + soft-piano BGM。

### 28. 生理警訊主題用警示樣式
**規則：** 喉嚨酸痛 / 氣息不足 / 聲帶保養等生理警訊主題，用 warning-red-gold。  
**原因：** 「身體在受傷」是嚴肅警訊，警示樣式有戲劇張力推動觀眾繼續看。

### 29. Hook 跟主題不匹配時的 SOP
**規則：** Hook 素材主題跟主片概念不對應時：
1. 先 flag 不匹配，讓用戶決定 (A) 換素材 (B) 換主題 (C) 硬剪加文字銜接
2. 選 (C) 時保留原片燒字當權威對照組（「連大咖都 X / 何況你」）
3. NLP 生底部銜接文案做語意橋接
4. Hook 最後 0.4s ffmpeg `afade=t=out:st=...:d=0.4` 音頻軟轉場 + 視覺 fade
5. 頂部標題押韻主片關鍵句

---

## 🎨 特效極性（正/負分離）

### 30. 症狀/觀察句不套 impact 特效
**規則：** 描述觀眾正在經歷的現象（「脖子就先緊了」「聲音還沒出來」）**不**套任何 impact 特效。  
**原因：** 這些是診斷句，不是成就也不是傷害，讓字幕說話。

### 31. Positive 只用在技巧/解法句
**規則：** 「看清楚」「搞懂」「省時間」「對的方式」等明確技巧/解法句才套 positive 特效。  
**Positive variants 三種：** speed-lines / gold-ring / emoji-slam，按 `positiveMoments` 順序輪替**不重複**，每個配不同 SFX。

### 32. Negative 只用在主動傷害句
**規則：** 「在磨」「消耗你」「硬撐下去」「越磨越薄」等描述進行中傷害的句子才套 negative 特效。  
**錯誤：** 問句「聲帶在不在硬撐？」**不是**負面，不要套。  
**錯誤：** 混合句（「喉嚨是鬆的，繼續硬撐下去」）也不列 negative，會看起來矛盾。

### 33. Negative 設計簡潔強烈，不花俏
**規則：** 只用 grayscale + 暗角 + 負面音效（音量 0.12）。**不**用紅 badge / 裂紋 / 粒子 / 抖動。  
**原因：** Badge 突兀，「灰階本身已經是強訊號，不需要再疊 badge 說『這是錯的』」。

### 34. Negative variant 機制（多支影片避免重複）
**規則：** `DynamicVideo.negativeVariants` 按 `negativeMoments` 順序指定 variant：
- **REVELATION（首次揭露）** → `ghost-echo`（雙層 OffthreadVideo + 半透明副本位移 + 冷藍調）
- **CLIMAX（最後高潮）** → `chromatic-drift`（雙 RGB drop-shadow）
- **保守 fallback** → `grayscale`

### 35. ghost-echo 雙層別為了 preview 流暢削弱
**規則：** ghost-echo 疊兩層 OffthreadVideo + `mix-blend-mode: screen` + blur 5 + 位移 28px。Studio 預覽會卡 1-2 幀，但 render offline 完全順。  
**原因：** Remotion Studio 是瀏覽器 real-time decode，會因 GPU 壓力卡幀；offline render 逐幀輸出每幀允許任意 decode 時間。**不要為了預覽流暢度犧牲成品視覺強度**，用戶看 preview 只是確認方向不是流暢度。

### 36. impact SFX 音量 0.12（不是 0.3）
**規則：** 所有 impact SFX volume 統一 0.12。  
**原因：** 0.3 用戶反饋「音效太重太突兀」。

### 37. 三個 positive variant 配不同 SFX
**規則：** speed-lines = sparkle / gold-ring = chime / emoji-slam = slam，不重複。  
**原因：** 視覺不一樣音效一樣很怪。

### 38. ghost-echo 配雙層 SFX
**規則：** ghost-echo 主 SFX `Ghostly whoosh passing` + 副 `impact_negative` 疊播。chromatic-drift 用 single SFX `impact_warning`。  
**原因：** 用戶反饋「沒有多重聲音」期待靈魂抽離音效不是通用 impact。

### 39. ImpactEffects negative branch 只觸發 SFX
**規則：** Negative variant 機制下，畫面效果由 `DynamicVideo` 處理，`ImpactEffects` 只播 SFX 不疊任何畫面元素。

### 40. 從乾淨 SFX 庫取音效
**規則：** 不從有背景音樂的影片剪音效，只從 mixkit / opengameart / freesound 取。  
**原因：** 從影片剪會帶到對方人聲/音樂，不乾淨。

---

## 🎵 BGM 選擇

### 41. BGM 必須先做爆款研究
**規則：** 不從舊清單直接選，每支影片去 TikTok/Reels 找相似主題的爆款分析他們用什麼 mood → 找對應素材。

### 42. 避開 bouncy ukulele / upbeat pop
**規則：** 不用 Happy Bee 類型 BGM。  
**原因：** 用戶反饋「太吵」、跟專業診斷 tone 不合。  
**也避：** 任何有明顯人聲/合唱的 BGM（會搶走教學語音）。

### 43. 不要連續兩支用同一首 BGM
**規則：** 每支新影片換 BGM。

### 44. BGM 音量 0.30（不是 0.25）
**規則：** `CONFIG.bgm.volume = 0.30`。  
**原因：** 0.25 用戶反饋「再大一點點不要大太多」。

### 45. 題材 × mood 對應
| 題材 | 推薦 mood |
|------|----------|
| 警示主題（警告 / 受傷 / 損壞）| ambient / soft-piano |
| 節奏 / 活力 / 舞台類 | gentle-electronic / lo-fi |
| 高音 / 走音 / 衝擊類 | cinematic |
| 情緒 / 反思 / 心理類 | soft-piano / ambient |

---

## ✂️ Jump Cut

### 46. Jump Cut 每句尾剪 100ms（不是 180ms）
**規則：** TAIL_TRIM = 100ms。  
**原因：** 180ms 會吃掉細弱字尾（樣 / 投入 / 僵掉）。100ms 留 80ms buffer。

### 47. 最後一句不剪 tail
**規則：** `i == len(items) - 1` 時 `seg_end = source_video_duration`（ffprobe 取得）。  
**原因：** CTA 句「我傳給你」尾音對觀眾感受最重要。

### 48. 連貫敘事可跳過 jump cut
**規則：** SRT 相鄰句時間戳 gap = 0（句尾 = 下句首，無停頓）→ 跳過 jump cut，只做 tpad + re-encode。  
**原因：** 180ms / 100ms 都會切破句尾。

### 49. SRT lastEnd 必須對齊實際 mp4 duration
**規則：** ffmpeg jump cut 完成後，**SRT 最後一句 endTime + Root.tsx 的 MAIN_DURATION_S 都用 ffprobe 拿到的實際 mp4 duration**（不是 SRT 累積總長）。  
**原因：** ffmpeg concat 邊界對齊會多 0.3-0.5s，Remotion 在 SRT lastEnd 收尾 → 末句尾音被截。  
**訊號：** 用戶反饋「最後一句還沒講完影片就沒了」第一個查這個。

### 50. 最後一幀 tpad 凍結
**規則：** ffmpeg `tpad=stop_mode=clone:stop_duration=3` 凍結最後 3 秒 + `apad=pad_dur=3` 補音軌。  
**原因：** 最後一幀 jump-cut 突兀。CTA overlay 需要時間讓觀眾讀完 3 行。  
**對應：** `FullVideo.mainDurationFrames` 改用 `Math.ceil(lastEnd * fps)` tight，不要 `+ 90` padding。

### 51. 主片 fps 不同不用擔心
**規則：** 原片 25fps + CONFIG.composition.fps=30 也沒事。  
**原因：** OffthreadVideo 會自動處理 fps 轉換，Root.tsx 用 CONFIG fps（30）算 duration 即可。

---

## 🖼 Logo 模糊 / 字幕帶遮擋

詳見 `hook-sop.md` 第 4-6 節。重點摘要：

### 52. 雙層 gblur 比單層強
**規則：** `gblur=sigma=80, gblur=sigma=40`，不單層 sigma=50。  
**原因：** 單層留可讀殘影。

### 53. crop 寬度要 ≥ 文字區 + 150px buffer
**規則：** Logo 區域寬度不要卡死文字邊緣。

### 54. 整條字幕帶比個別字 robust
**規則：** 原片底部歌詞字幕帶（y:950-1060）整條 1080 全寬模糊，不只模糊個別字。  
**原因：** 字幕會隨時間換句，剪 Hook 不一定能避開切換瞬間，1 幀 leak 觀眾就看到。  
**例外：** 人物身體在中央時，整條全寬會遮腰部 → 改分 3 塊（左下/右上/右下）剛好遮文字 + 小 buffer，雙層 gblur sigma=60+30 即可。

### 55. 只用 ffmpeg crop+gblur，不要其他方法
**錯誤方法：** CSS backdrop-filter（位置對不準）/ drawbox（醜，蓋臉）/ Remotion 漸層遮蓋（位置不精確）。  
**唯一可靠：** ffmpeg crop+gblur+overlay 精準座標。

### 56. IG/媒體源頭頂部範圍 y=0-380（不是 y=0-300）
**規則：** 頂部燒字 + 頻道 logo 區擴大到 y=0-380。  
**原因：** 頻道 logo 通常在 y=265-330，y=0-300 漏掉。  
**buffer 原則：** 頂部範圍 = 燒字區域 + logo 範圍 + 50px buffer。

### 57. 中央飄字保留當對照組
**規則：** IG 媒體源頭的中央後製飄字（如「眼神超堅毅」）**不**遮，保留當「媒體後製對照組」。  
**原因：** 增加真實感（網民批評歌手 → 我們點出真因），不擋臉、不違和。

---

## 📥 素材下載

### 58. 抖音 yt-dlp 反爬解法
**規則：** 2026-04 後 yt-dlp 即使帶 chrome cookies 也擋。改用 Chrome MCP 開抖音真實 URL → `read_network_requests` 抓 `mime_type=video_mp4` 的 `*.douyinvod.com` URL → `curl -L -H "Referer: https://www.douyin.com/" -H "User-Agent: <Chrome UA>"`。  
**注意：** URL 有時效（`dy_q=` timestamp），1 小時內下完。

### 59. 表演者名字 verify
**規則：** 用戶給的表演者名字可能跟原片實際不符（記憶 mismatch）。下載後讀 Chrome tab title + 抽 4 frames @ 1.5/5/8/11s 確認 boundary。不符回問用戶。

### 60. Hook boundary 用視覺幀確認
**規則：** Whisper 對 live + 多人合唱 + 伴奏識別不準。改用視覺：抽密集幀（fps=2 共 14 張）找 climax 動作最強那一幀。  
**範例：** belt 動作最強 = 雙手高舉 + 嘴張開直視鏡頭。

### 61. 檔名只當 hint，以 SRT 內容為準
**規則：** Desktop 檔名「喉嚨緊繃酸痛.mp4」可能 SRT 出來其實是「共鳴／聲音薄飄」。Whisper 出 SRT 後才決定主題。  
**原因：** 檔名跟內容可能 mismatch。

### 62. IG Reel 直接 yt-dlp 不需直式轉換
**規則：** IG Reel 原本就是 1080x1920 30fps 直式 → 跳過 blur-fill 步驟。  
**Whisper：** IG Reel 音頻表現好，可精準轉錄歌詞 / word-level timestamps。

---

## 🤖 NLP / LLM 文案生成

### 63. NLP API prompt 用自然語言，不要 JSON-in-JSON
**規則：** 用自然語言句子描述情境，不用引號轉義堆 JSON 包 JSON。關鍵詞重複 3-5 次主題詞。  
**原因：** 太多轉義 NLP 會「知識庫沒對應」。

### 64. Hook 頂部標題必須給範本句法 + 實例
**規則：** prompt 必須含「第一行黃底黑字 13-18 字（人物+動作+節目）/ 第二行白底黑字 10-15 字（動詞+具體缺點+加號）」+ 實例。  
**原因：** 直接「設計兩行標題」會出文藝/問句（「淚水深埋的堅毅 / 真摯詮釋如何能更自然？」）— 不是要的新聞八卦感。

### 65. 用戶偏好「新聞八卦向」
**規則：** 避「淚水堅毅」「感情詮釋如何更自然」這種詩感／文藝；要「翻車現場」「遭批」「斷線」這類動詞 + 加號連接副標。可主動加碼第 4 組「新聞八卦向」給用戶比較。

### 66. CTA 留言版優先稀缺感風格
**規則：** 產 3 組（稀缺感/前提假設/社群認同），優先稀缺感（「限時免費領取教材」）。

### 67. NLP Hook 文案痛點 SOP
**規則：**
- 直接描述影片裡正在發生的失控狀態（不是觀眾自己的痛點）
- 列舉具體失控點（咬字糊+音準歪+節奏亂）
- 提問結尾觸發共鳴
- 用「翻車」（用戶喜歡）但避「大咖」「真相」「教幾招」

---

## 🎯 關鍵詞 / 高亮 pattern

### 68. Pattern order 規則
**規則：** highlightRules 物理順序直接決定 ACCENT_MAP emoji 觸發順序。substring 重疊的 patterns，**長/精準的必須排前面**。  
**範例：** 「錯誤位置」需在「錯位置」前；「沙啞」需在「都啞」前。

### 69. 每支新影片必須替換 ACCENT_MAP
**規則：** ACCENT_MAP patterns 必須跟 highlightRules 重複出現，否則 `current.text.includes(rule.pattern)` 不 match。  
**原因：** 上次主題的 patterns 在新主題不出現 → emoji 完全不顯示。

### 70. 按情緒分類 emoji
**規則：**
- negative ⚠️😰 / positive (KEY revelation) ✨💡 / bridge (CTA hint) 🎯
- 比例 ~18%（5 emoji on 28 lines），不要太滿。

### 71. CTA highlight props 加新 prop 同步 caller
**規則：** 加 component 新 props 時 grep 所有 caller 同步更新 propagation。  
**原因：** 加 `line1Highlights / line3Highlights` props 但 FullVideo.tsx 沒同步傳，顏色不生效。

---

## 🚨 渲染相關

詳見 `render-anti-jitter.md`。重點摘要：

### 72. OffthreadVideo 不用 Video
### 73. seededRandom 不用 Math.random()
### 74. 影片必須 ffmpeg 重新編碼修時間戳
### 75. 渲染加大快取
### 76. 不要 npx remotion render 跳過 preview
### 77. SRT lastEnd = 實際 mp4 duration

---

## ⚙️ 流程紀律

### 78. 先預覽再渲染
**規則：** 跑完 Root.tsx / HookSection / SRT 調整之後，必須先啟 `npx remotion studio --port 3333` 給用戶瀏覽預覽，**不要**直接 `npx remotion render` 匯出 MP4。  
**原因：** 預覽階段改 1 字 = 免重跑；渲染後改 1 字 = 重渲 30 分鐘 + 兩版 MP4 浪費。  
**例外：** 沒有，永遠不要偷跑 render。

### 79. 兩個 Composition 一起做
**規則：** 每支影片建立兩個 Composition（`<Project>-LINE` + `<Project>-Comment`），兩個只有最後一句 CTA 字幕不同。  
**原因：** 一次渲兩版省時。

### 80. 每反饋分類，不要混改
**規則：** 用戶反饋來：
- **單支影片問題** → 只改 Root.tsx 的 props
- **模板規則問題** → 改 video-config.ts + CLAUDE.md/SKILL.md + lessons.md + memory  

**原因：** 模板規則只在「以後所有影片都改」時才動 config。

### 81. 每個閘門停下等用戶確認
**規則：** 不要連環跑到渲染。明確說「請 review 確認後告訴我可以進下一步」。  
**Why：** 用戶反饋「要先開 Remotion 的預覽界面給我看，不要直接匯出影片的成品」。

---

## 📊 持續學習疊代

### 82. 每反饋寫進對應分類
**規則：** 每次踩坑 → 加進這份 lessons.md 對應分類。  
**規則：** 每次解決新問題 → 寫進對應 reference。  
**原則：** 模板要越用越好，不是停留在當下狀態。

### 83. 不要憑空模仿，網路調查優先
**規則：** 加新效果前必須去網路找 3-5 支爆款（10 萬+），分析共通元素再複刻。  
**用戶原話：** 「你靠模仿自己去把它做出來，效果會非常非常爛」  
**步驟：**
1. 抖音/TikTok/Reels/YouTube Shorts 搜尋該類效果
2. 截圖存 `reference/viral-samples/[類型]/`
3. 分析共同視覺元素 → 提取核心設計
4. 複刻成 Remotion 組件，註解標註參考來源

### 84. 變化是為了避免重複，不是塞滿
**規則：** 一支影片最多 2 個負面 + 2-3 個正面 + 2-3 emoji。節奏優先於花俏。  
**原則：** 核心不變（字體 / 品牌色 / 字幕風格 / BGM 來源），核心可變（特效類型 / badge 文字 / 音效 / Hook 組合）。
