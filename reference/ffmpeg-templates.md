# ffmpeg 指令模板（直接複製改用）

所有 ffmpeg 指令的 reference template。具體參數視影片實際內容調整。

---

## ① 提取音頻給 Whisper

```bash
ffmpeg -i source.mp4 -vn -acodec pcm_s16le -ar 16000 -ac 1 audio.wav
```

**用途：** 抽出 16kHz mono PCM 給 Whisper（最佳 input format）。

---

## ② 下載 + 直式轉換 Hook 影片（blur-fill 背景）

### YouTube / Bilibili 等支援來源
```bash
# 下載指定段落
yt-dlp -f "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best" \
  --download-sections "*開始秒-結束秒" \
  -o hook_raw.mp4 \
  "YouTube_URL"
```

### IG Reel
```bash
yt-dlp -f "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best" \
  -o hook_full.mp4 \
  "https://www.instagram.com/reel/<id>/"
```
**注意：** IG Reel 通常已是 1080x1920 30fps 直式 → 跳過 blur-fill 步驟。

### 抖音（2026-04 後反爬，yt-dlp 失敗）
不能用 yt-dlp。改用 Chrome MCP：
1. 開抖音真實 URL `https://www.douyin.com/video/<id>`
2. `read_network_requests` 抓 `mime_type=video_mp4` 的 `*.douyinvod.com` URL
3. `curl -L -H "Referer: https://www.douyin.com/" -H "User-Agent: <Chrome UA>"` 下載
4. URL 1 小時內下完（`dy_q=` timestamp）

### 橫式 → 直式 blur-fill 轉換
```bash
ffmpeg -ss 起始 -t 時長 -i hook_raw.mp4 \
  -filter_complex "\
    [0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=25:5[bg]; \
    [0:v]scale=1080:-2[fg]; \
    [bg][fg]overlay=(W-w)/2:(H-h)/2[out]" \
  -map "[out]" -map 0:a \
  -c:v libx264 -preset medium -crf 20 -c:a aac -b:a 128k hook.mp4
```

**參數說明：**
- `boxblur=25:5` — 背景模糊強度（25 像素半徑，5 次迭代）
- `scale=1080:-2` — 主影片寬度 1080，高度自動算（保持比例）

---

## ③ Logo 模糊（雙層 gblur）

### Step 1：找 logo 精確座標
```bash
ffmpeg -i hook.mp4 -vf "select=eq(n\,60),crop=350:120:0:710" \
  -vsync vfr -q:v 2 /tmp/logo_check.jpg
```
看 `/tmp/logo_check.jpg`，調整 `crop=W:H:X:Y` 直到精確框住 logo。

### Step 2：精準模糊
```bash
ffmpeg -y -i hook.mp4 -filter_complex "
  [0:v]split=3[main][c1][c2];
  [c1]crop=W:H:X:Y,gblur=sigma=80[b1];
  [c2]crop=W:H:X:Y,gblur=sigma=40[b2];
  [main][b1]overlay=X:Y[t1];
  [t1][b2]overlay=X:Y[out]
" -map "[out]" -map 0:a -c:v libx264 -crf 20 -c:a copy hook_clean.mp4
```

**規則：**
- logo 區域寬度 ≥ 實際文字寬度 + 150px buffer
- sigma 用**雙層**（80 + 40），不要單層 50（會留可讀殘影）

---

## ④ Hook 原片字幕帶遮擋（整條全寬）

```bash
# 整條底部歌詞字幕帶模糊（y:950-1060）
ffmpeg -y -i hook.mp4 -filter_complex "
  [0:v]split=2[main][c1];
  [c1]crop=1080:110:0:950,gblur=sigma=60,gblur=sigma=30[b1];
  [main][b1]overlay=0:950[out]
" -map "[out]" -map 0:a -c:v libx264 -crf 20 -c:a copy hook_clean.mp4
```

**為什麼整條遮：** 字幕會隨時間換句，1 幀 leak 觀眾就看到。

---

## ⑤ IG/媒體源頭頂部 + 底部水印模糊

情境：IG Reel / 微博 / 抖音轉發類媒體頻道，頂部有燒字 + 頻道 logo，底部有水印。

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

**規則：**
- 頂部範圍 y=0-380（不是 0-300）— 含頻道 logo + 50px buffer
- **中央飄字保留不遮**（增加「媒體後製」對照感）
- 底部水印 y=1680-1920 雙層 gblur sigma=60+30
- `-af afade` 最後 0.4s 音頻軟轉場

---

## ⑥ 人物身體在中央時的 logo 模糊（分塊小區域）

vocal-resonance 主題用「整條遮 robust」，但**人物身體在中央時整條全寬會遮腰部** → 改分 3 塊。

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

**參數規則：**
- 分塊用較弱雙層 gblur sigma=60+30（不需要 80+40 / 100+50）
- 每塊 crop 剛好遮文字 + 小 buffer
- 中央人物保留

---

## ⑦ Jump Cut（每句尾剪 100ms，最後一句不剪）

### Python 模板（jumpcut.py）
```python
import subprocess
from pathlib import Path

SRC_MP4 = Path("source.mp4")
SRT_FILE = Path("source.srt")
OUTPUT = Path("source_tight.mp4")
TAIL_TRIM = 0.10  # 100ms

# 取得原片實際 duration（用 ffprobe）
src_dur = float(subprocess.check_output([
    "ffprobe","-v","error",
    "-show_entries","format=duration",
    "-of","default=nw=1:nk=1",
    str(SRC_MP4)
]).strip())

# 解析 SRT → items: [(idx, start, end, body), ...]
# ... (SRT parser code)

# 計算每段 trim 時段
filter_parts = []
for i, (idx, start, end, body) in enumerate(items):
    seg_start = start
    if i == len(items) - 1:
        seg_end = src_dur  # 最後一句不剪 tail
    else:
        seg_end = max(start + 0.05, end - TAIL_TRIM)
    filter_parts.append(f"[0:v]trim=start={seg_start}:end={seg_end},setpts=PTS-STARTPTS[v{i}];")
    filter_parts.append(f"[0:a]atrim=start={seg_start}:end={seg_end},asetpts=PTS-STARTPTS[a{i}];")

# concat
concat_v = "".join(f"[v{i}]" for i in range(len(items)))
concat_a = "".join(f"[a{i}]" for i in range(len(items)))
filter_parts.append(f"{concat_v}concat=n={len(items)}:v=1:a=0[outv];")
filter_parts.append(f"{concat_a}concat=n={len(items)}:v=0:a=1[outa]")

filter_complex = "".join(filter_parts)

subprocess.run([
    "ffmpeg","-y","-i", str(SRC_MP4),
    "-filter_complex", filter_complex,
    "-map","[outv]","-map","[outa]",
    "-c:v","libx264","-crf","18","-c:a","aac",
    str(OUTPUT)
], check=True)
```

**規則：**
- TAIL_TRIM = 100ms（不是 180ms — 會吃細弱字尾）
- 最後一段 `seg_end = src_dur`（不剪 tail，保留 CTA 句完整）

---

## ⑧ 重新編碼修時間戳（防渲染抖動）

```bash
ffmpeg -i input.mp4 \
  -c:v libx264 -preset medium -crf 18 \
  -c:a aac -b:a 128k \
  output.mp4
```

**何時做：**
- Hook 模糊處理後（modify 過 video stream）
- Jump Cut 完成後
- 任何 source mp4 進 Remotion 之前

**原因：** 修復時間戳避免 OffthreadVideo 提幀不準。

---

## ⑨ 最後一幀 tpad 凍結

```bash
ffmpeg -i source_tight.mp4 -filter_complex "
  [0:v]tpad=stop_mode=clone:stop_duration=3[v];
  [0:a]apad=pad_dur=3[a]
" -map "[v]" -map "[a]" \
  -c:v libx264 -crf 18 -c:a aac \
  source_tight_padded.mp4
```

**用途：** 最後一幀 clone 延長 3 秒，讓 CTA overlay 停留到觀眾讀完。

---

## ⑩ 提取單幀（找座標 / 確認 boundary）

### 提取單幀
```bash
ffmpeg -i video.mp4 -vf "select=eq(n\,60)" -vsync vfr -q:v 2 frame_60.jpg
```

### 提取密集幀（每 0.5s 一張）找 climax
```bash
ffmpeg -i hook.mp4 -vf "fps=2" frames_%03d.jpg
```

**用途：** Whisper 對 live + 多人合唱 + 伴奏識別不準時，改用視覺找 climax 動作最強那一幀。

---

## ⑪ ffprobe 取 duration

```bash
ffprobe -v error \
  -show_entries format=duration \
  -of default=nw=1:nk=1 \
  source_tight.mp4
```

**用途：** 取得 jump cut 後的實際 mp4 duration → 寫進 SRT 最後一句 endTime + Root.tsx 的 MAIN_DURATION_S。

---

## ⑫ 渲染 Remotion（兩個 Composition）

```bash
# 預覽（必須先做）
pkill -f remotion
npx remotion studio src/index.ts --port 3333

# 用戶在 http://localhost:3333/<CompositionId> 確認後...
# 渲染兩版
npx remotion render src/index.ts <Project>-LINE \
  --output=output_LINE.mp4 \
  --codec=h264 \
  --timeout=120000 \
  --offthreadvideo-cache-size-in-bytes=4000000000

npx remotion render src/index.ts <Project>-Comment \
  --output=output_Comment.mp4 \
  --codec=h264 \
  --timeout=120000 \
  --offthreadvideo-cache-size-in-bytes=4000000000
```

---

## ⑬ Bundle cache 清除（新加 public/ 資產報 404 時）

```bash
rm -rf /var/folders/*/remotion-webpack-bundle-*

# 渲染加 --public-dir
npx remotion render ... --public-dir=/abs/path/to/public
```

---

## ⑭ Mixkit 自動下載 SFX/BGM（JS dispatch）

Mixkit 下載按鈕 outer DIV click 不 propagate 到 `.download-button--icon` button 的 event handler。要 dispatch 完整 PointerEvent + MouseEvent sequence。

```javascript
// Chrome console / browser MCP 執行
const titles = document.querySelectorAll('h2, h3');
const target = Array.from(titles).find(el => el.textContent.includes('<TRACK_TITLE>'));
const row = target.closest('[data-track]') || target.parentElement;
const btn = row.querySelector('button.download-button--icon');

const rect = btn.getBoundingClientRect();
const cx = rect.left + rect.width / 2;
const cy = rect.top + rect.height / 2;

['pointerdown', 'mousedown', 'pointerup', 'mouseup', 'click'].forEach(type => {
  const EvtCtor = type.startsWith('pointer') ? PointerEvent : MouseEvent;
  btn.dispatchEvent(new EvtCtor(type, {
    bubbles: true, cancelable: true,
    clientX: cx, clientY: cy
  }));
});
```
