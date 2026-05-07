# Quickstart — 30 秒上手

## 1️⃣ 安裝（一行）

```bash
git clone https://github.com/jaychou6868/videocut.git ~/.claude/skills/videocut
```

## 2️⃣ 驗證

打開 Claude Code，在對話打：

```
/videocut
```

看到「Videocut — Remotion 短影片自動後製工作流」就對了。

## 3️⃣ 第一支影片

需要先準備好（前置需求，缺一不可）：

| 必備 | 怎麼裝 |
|------|--------|
| Remotion 專案 starter | `npx create-video@latest`，或 fork 現成模板 |
| ffmpeg | `brew install ffmpeg` |
| yt-dlp | `brew install yt-dlp` |
| whisper | `pip install openai-whisper` |
| LLM API key | OpenAI 或 Claude，自己的就好 |

然後跑：

```
/videocut <主題> <原片路徑> <Hook URL+秒數>
```

或無參數 `/videocut` 讓它互動問你。

## 4️⃣ 三大原則（不要違反就好）

1. **手機安全區** — 影片給手機看，邊緣會被 IG/TikTok UI 蓋
2. **網路調查優先** — 加新效果先去抖音/TikTok 找爆款，不要憑空想
3. **少而有力** — 一支影片最多 2 個負面 + 2-3 個正面 + 2-3 emoji

## 5️⃣ 下一步

- 完整流程說明 → [README.md](README.md)
- 8 步驟詳解 → [SKILL.md](SKILL.md)
- 所有踩過的坑 → [reference/lessons.md](reference/lessons.md)
- 換領域用（不是聲樂）→ [reference/topic-config.md](reference/topic-config.md) 最末段

---

有問題回來戳作者就好。
