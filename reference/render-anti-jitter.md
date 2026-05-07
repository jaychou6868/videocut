# 渲染防抖 6 條規則（必讀，違反必出問題）

Remotion 渲染抖動 / 閃爍 / 黑屏的所有踩坑根因。

---

## 1. 影片組件：必須用 OffthreadVideo

```tsx
// ✅ 正確
import { OffthreadVideo } from "remotion";
<OffthreadVideo src={staticFile("video.mp4")} />

// ❌ 錯誤 — 渲染時會抖動（預覽正常但渲染出來人頭一直抖）
import { Video } from "remotion";
<Video src={staticFile("video.mp4")} />
```

**原因：** `<Video>` 依賴瀏覽器 seek 事件，渲染時不保證當前幀已正確繪製。`<OffthreadVideo>` 用 ffmpeg 逐幀提取，幀精確。

---

## 2. 禁止 Math.random()

```tsx
// ❌ 錯誤 — 並行渲染每個 worker 產生不同值，特效每幀閃爍
const size = 20 + Math.random() * 60;

// ✅ 正確 — 確定性偽隨機，所有 worker 相同結果
function seededRandom(seed: number): number {
  const x = Math.sin(seed * 9301 + 49297) * 233280;
  return x - Math.floor(x);
}
const size = 20 + seededRandom(i * 7 + 4) * 60;
```

**原因：** Remotion 並行渲染每個 worker 獨立執行 React，`Math.random()` 在每個 worker 產生不同值 → 特效每幀位置不同 → 閃爍。

**適用：** ShatterEffect 碎片位置 / MangaText 抖動 / 任何粒子系統。

---

## 3. 輸入影片必須重新編碼

```bash
ffmpeg -i input.mp4 -c:v libx264 -preset medium -crf 18 -c:a aac -b:a 128k output.mp4
```

**原因：** 原始下載的影片時間戳可能不規則（VBR / B-frame / GOP 邊界跑掉），OffthreadVideo 用 ffmpeg 提幀時會不準。重新編碼用 libx264 固定 CRF 修復時間戳。

**何時做：** Hook 下載完轉直式之後，做 logo 模糊之前；或主片 jump cut 之後。

---

## 4. 渲染指令加大快取

```bash
npx remotion render src/index.ts <CompositionId> \
  --output=output.mp4 \
  --codec=h264 \
  --timeout=120000 \
  --offthreadvideo-cache-size-in-bytes=4000000000
```

**原因：** OffthreadVideo 提幀有 cache，預設太小會頻繁解碼 → 慢且可能抖。4GB cache 對中等長度影片夠用。

**新加 public/ 資產報 404 時：**

```bash
rm -rf /var/folders/*/remotion-webpack-bundle-*
npx remotion render ... --public-dir=/abs/path/to/public
```

---

## 5. 最後一幀不 jump — tpad 凍結

```bash
# 凍結 main source 最後 3 秒 + 同時補音軌 3 秒
ffmpeg -i source_tight.mp4 -filter_complex "
  [0:v]tpad=stop_mode=clone:stop_duration=3[v];
  [0:a]apad=pad_dur=3[a]
" -map "[v]" -map "[a]" -c:v libx264 -crf 18 -c:a aac source_tight_padded.mp4
```

**原因：** 影片最後一幀 jump-cut 突兀。CTA overlay 需要時間讓觀眾讀完 3 行。  
**對應：** `FullVideo.mainDurationFrames` 改用 `Math.ceil(lastEnd * fps)` tight，**不要 `+ 90` padding**（會超過 video duration → 黑屏）。

---

## 6. SRT lastEnd 必須對齊實際 mp4 duration

ffmpeg jump cut concat 出來的實際 mp4 duration 通常**比 SRT 計算總長多 0.3-0.5s**（concat keyframe / GOP 邊界對齊）。後果：Remotion 在 SRT lastEnd 收尾，影片最後 0.3-0.5s 沒播 → 末句尾音被截。

**SOP：**

1. ffmpeg jump cut 完成後 → ffprobe 取得實際 mp4 duration：
```bash
ffprobe -v error -show_entries format=duration -of default=nw=1:nk=1 source_tight.mp4
```

2. SRT 最後一句 endTime **改用實際 mp4 duration**（不是 SRT 計算的累積總長）

3. Root.tsx 的 `MAIN_DURATION_S` 也用實際 mp4 duration

**用戶反饋訊號：** 「最後一句『我傳給你』還沒講完，影片就沒了」「可不可以完全不要截？就是最後一幀。」 — 出現這種反饋第一個查 SRT lastEnd = 實際 mp4 duration。

---

## 7. 不要為了修抖動刪減效果

**規則：** 抖動問題在底層組件（Video vs OffthreadVideo），不在效果本身。

**錯誤反應：** 看到抖動 → 刪 zoom / 刪粒子 / 刪動畫 → 抖動還在。  
**正確反應：** 換成 OffthreadVideo + seededRandom + 重編碼影片，三件齊全才會根治。

---

## 8. Studio preview 卡 ≠ render 會卡

**規則：** Remotion Studio 預覽是瀏覽器 real-time 渲染，會因 GPU/decode 壓力短暫卡幀；`remotion render` 是 offline 逐幀輸出，每幀允許任意時間 decode，視覺完全不受影響。

**重要：** 當視覺效果（特別是疊 OffthreadVideo / mix-blend-mode / heavy filter）在預覽會卡時，**保留強參數不要削弱**，告訴用戶「預覽卡但成品順」即可。

**何時遇到：**
- 疊多層 OffthreadVideo（ghost-echo 效果）
- mix-blend-mode: screen
- 多層 drop-shadow filter chain
- Multiple `<Audio>` 疊加

**怎麼處理：**
- 用戶反饋 Studio 預覽「卡」「lag」時，先判斷：
  - (a) 只是 real-time decode 壓力 → 跟用戶說「render 出來不會卡」不要改 code
  - (b) 有實際 bug / 死迴圈 → 才去改
- 加註解：特效 code 裡明確寫「Studio 預覽會卡但 render offline 不受影響」，未來不會再誤改

**錯誤示範（不要做）：** 為了 Studio 流暢，把 ghost-echo 從雙層改單層 + 拿掉 mix-blend-mode → render 出來「沒有雙層幽靈感」要重 render。

---

## 9. 不要直接 npx remotion render 跳過 preview

**規則：** 跑完 Root.tsx / HookSection / SRT 調整之後，必須先啟 Remotion Studio 給用戶瀏覽預覽，**不要**直接 `npx remotion render` 匯出 MP4。

```bash
# ✅ 先預覽
pkill -f remotion
npx remotion studio src/index.ts --port 3333
# 用戶在 http://localhost:3333/<CompositionId> 看
# ⚠️ 等用戶說「OK 可以渲了」才進下一步

# ❌ 不要直接渲染
npx remotion render ...  # ⚠️ 跳過 preview = 錯字重渲 = 浪費時間
```

**Why：** 預覽階段改 1 字 = 免重跑；渲染後改 1 字 = 重渲 30 分鐘 + 兩版 MP4 浪費。
