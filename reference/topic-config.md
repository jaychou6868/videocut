# 主題 → 模板配置查閱表

每個影片主題對應的 Hook 樣式 / Positive variant 順序 / BGM mood / crackFrame 對齊規則。

**使用方式：** 做新影片前先查這張表找主題對應配置。沒對應的主題 → 用最接近的主題當起點，做完後評估要不要補進此表。

**這份表的範例領域是聲樂教學。其他領域用戶請替換成自己的主題（例：健身 → squat-form / pull-up / cardio；料理 → knife-skills / heat-control 等）。**

---

## 主題分類

### 生理警訊類 → warning-red-gold 樣式
喉嚨酸痛 / 氣息不足 / 聲帶保養 / 高音聲帶硬扛

### 表現失控類 → warning-red-gold 樣式
高音唱不上去 / 走音 / 破音 / 節奏抓不準

### 心理脆弱類 → 無中央大字（原片燒字當對照組）
上台緊張 / 不敢開口 / 唱歌沒感情

### 共鳴/感受類 → 無中央大字（原片燒字當對照組）
共鳴 / 聲音薄飄 / KTV 聲音散

---

## 完整查閱表（聲樂領域範例）

| 主題 | Hook 中央大字樣式 | Positive variant 先手順序 | BGM mood | crackFrame 對齊到 |
|------|------------------|-----------------------|---------|----------------|
| **throat-strain**（喉嚨酸痛）| warning-red-gold（紅底金邊 + ⚠⚠ + 脈動紅光 + 抖動）| gold-ring → speed-lines → emoji-slam | ambient / soft-piano | 歌手唱出「害怕／疼／撐不住」的 word onset |
| **high-notes**（高音唱不上去）| warning-red-gold | speed-lines → emoji-slam → gold-ring | cinematic（稍強）| 破音／飆高音卡死的 onset |
| **breath-support**（氣不夠用）| warning-red-gold | gold-ring → speed-lines → emoji-slam | ambient / soft-piano | 換氣急促／斷氣 onset |
| **rhythm-timing**（節奏抓不準）| description（柔性樣式）| emoji-slam → speed-lines → gold-ring | gentle-electronic / lo-fi | 拍點跑掉的那一拍 |
| **pitch-accuracy**（音不準／走音）| warning-red-gold | speed-lines → gold-ring → emoji-slam | cinematic | 走音那一個音的 onset |
| **emotion-expression**（唱歌沒感情）| **無中央大字**（confidence-stage 策略）| speed-lines → gold-ring → emoji-slam | soft-piano | crackFrame=9999 禁用 |
| **confidence-stage**（上台緊張／不敢開口）| **無中央大字**（原片燒字當對照組 + 自家 headline 在頂部）| gold-ring → speed-lines → emoji-slam | soft-piano | crackFrame=9999 禁用 |
| **vocal-health**（聲帶保養）| warning-red-gold | gold-ring → speed-lines → emoji-slam | ambient | 嘶吼／喉嚨用力過度的瞬間 |
| **vocal-resonance**（共鳴／聲音薄飄）| **無中央大字**（原片燒字當對照組）| gold-ring → speed-lines → emoji-slam | cinematic-piano-strings | crackFrame=9999 禁用 |
| **high-notes + vocal-health 複合**（高音→聲帶硬扛→沙啞）| warning-red-gold（**不寫「警報!」開頭**）| gold-ring → speed-lines → emoji-slam | dark-ambient | Hook 失控 climax 視覺 onset |

---

## 樣式說明

### Hook 中央大字「warning-red-gold」
- 樣式：紅底 + 金邊 + ⚠⚠ + 脈動紅光 + 輕微抖動
- 入場：crackFrame + 15 幀（crack 後 0.5s）
- 用於：生理警訊類 + 表現失控類主題
- **不寫「警報！」開頭**（樣式本身已 ⚠⚠ + 紅底金邊脈動，不需要文字再強調）

### Hook 中央大字「description」
- 待建樣式（非警示類主題）
- 目前**沒有**對應組件，遇到這類主題要先補一個描述感／反思感的樣式（淡色背景 + 柔性邊框，無震撼元素）

### 「無中央大字」配置
- 用於：心理脆弱類 + 共鳴/感受類主題
- 設定：`bigText="" bigText2="" mangaText="" reactionText="" crackFrame=9999`
- 自家 NLP-生 headline + subheadline 疊頂部
- 中央保留原片燒字當「媒體後製對照組」
- 心理恐懼類走共鳴而非警示，警示讓觀眾覺得「被指責」→ 划走率升高

---

## Positive variant 機制

3 種 variant 按 `positiveMoments` 陣列順序輪替**不重複**，每個配不同 SFX：

| Variant | 視覺 | SFX |
|---------|------|-----|
| `speed-lines` | 白色速度線 + 金色星星粒子 | impact_sparkle.mp3 |
| `gold-ring` | 金色脈動環 + 閃光 | impact_chime.mp3 |
| `emoji-slam` | emoji 大字 slam 進場 | impact_slam.mp3 |

**輪替規則：** `posIdx % positiveVariantOrder.length`

---

## Negative variant 機制

`DynamicVideo.negativeVariants` 按 `negativeMoments` 順序指定 variant：

| Variant | 視覺 | 實作 | SFX | 適合情緒 |
|---------|------|------|-----|---------|
| `grayscale`（legacy）| 去飽和黑白化 + vignette | 單層 `filter: grayscale()` | impact_negative | 錯誤／違反規則感 |
| `ghost-echo`（強）| 主影片 + 半透明副本向左下位移 15-28px + blur 2.5-5px + 冷藍調 | **疊兩層** OffthreadVideo | ghost_whoosh + impact_negative（雙層）| 能量流失／共鳴抽離 |
| `chromatic-drift`（收尾）| 紅藍通道分離呼吸式位移 + 輕微去飽和 | 單層 `filter: drop-shadow(...)` | impact_warning | 訊號崩解／climax 不穩 |

**使用規則：**
- 每支影片 `negativeMoments` 至多 2 個，`negativeVariants` 對應 2 個
- **REVELATION（首次揭露）** → `ghost-echo`（強，視覺衝擊）
- **CLIMAX（最後高潮）** → `chromatic-drift`（收尾）
- 若只有 1 個 negative，可用 `grayscale` fallback

---

## BGM mood 對應

| Mood | 適用主題 | 來源 |
|------|---------|------|
| ambient / soft-piano | 警示主題（喉嚨酸痛 / 氣息不足 / 聲帶保養）| Kevin MacLeod (incompetech.com) |
| gentle-electronic / lo-fi | 節奏 / 活力主題 | Mixkit / Pixabay |
| cinematic | 高音 / 走音主題 | Kevin MacLeod cinematic 系列 |
| soft-piano / ambient | 情緒 / 反思主題 | Kevin MacLeod / Mixkit |
| dark-ambient | vocal-health 嚴重警示 | Anguish by Kevin MacLeod |
| cinematic-piano-strings | vocal-resonance | Silent Descent by Eugenio Mininni |

**規則：**
- 每支新影片要重新做爆款研究（去 TikTok/Reels 找相似主題的爆款分析他們用什麼 mood）
- 不從舊清單直接選
- 不要連續兩支用同一首
- 避開 bouncy ukulele / upbeat pop / 有人聲合唱的 BGM

---

## 主題不在表中的處理

如果用戶要的主題沒在表中（例：「舞台表情管理」「咬字清晰度」），步驟：

1. 找最接近的已知主題當起點
2. 告訴用戶「這個主題還沒正式加進查閱表，我先按 [最接近主題] 的配置做」
3. 影片做完用戶滿意後 → 補進表中（更新此 reference）

---

## 換領域使用此 skill

要把這份 skill 用在其他領域（不是聲樂），用戶需要：

1. **替換主題清單** — 改成自己領域的主題（例：健身教練 → squat-depth / breathing-pattern / progressive-overload）
2. **保留分類概念** — 生理警訊 / 表現失控 / 心理脆弱 / 共鳴感受這四大類在大部分領域都通用
3. **保留樣式對應** — warning-red-gold 給生理/失控；無中央大字給心理/共鳴
4. **重新做 BGM mood 對應** — 看自己領域影片的 tone（健身 BGM 通常 upbeat，跟聲樂的 ambient 完全不同）
5. **重新做 NLP prompt 校對詞** — 改成你的領域術語

範例（健身教練版）：

| 主題 | Hook 中央大字 | Variant 順序 | BGM mood |
|------|--------------|-------------|---------|
| squat-depth-fail（深蹲深度不夠）| warning-red-gold | gold-ring → speed-lines | gym-energetic |
| pull-up-form-break（引體向上姿勢崩）| warning-red-gold | speed-lines → emoji-slam | rock-cinematic |
| cardio-fatigue（有氧太累放棄）| 無中央大字 | gold-ring → speed-lines | melodic-electronic |
| body-image-anxiety（不敢上健身房）| 無中央大字 | gold-ring → speed-lines | warm-acoustic |
