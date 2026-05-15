---
name: youtube-content
description: "YouTube transcripts to summaries, threads, blogs."
platforms: [linux, macos, windows]
---

# YouTube Content Tool

## When to use

Use when the user shares a YouTube URL or video link, asks to summarize a video, requests a transcript, or wants to extract and reformat content from any YouTube video. Transforms transcripts into structured content (chapters, summaries, threads, blog posts).

Extract transcripts from YouTube videos and convert them into useful formats.

## Setup

```bash
pip install youtube-transcript-api
```

Optional fallback for videos with captions/transcripts disabled:

```bash
pip install yt-dlp faster-whisper
```

Use this only when transcript APIs fail and the user still wants the video understood. Prefer transcript extraction first because it is faster and preserves better timestamps.

## Helper Script

`SKILL_DIR` is the directory containing this SKILL.md file. The script accepts any standard YouTube URL format, short links (youtu.be), shorts, embeds, live links, or a raw 11-character video ID.

```bash
# JSON output with metadata
python3 SKILL_DIR/scripts/fetch_transcript.py "https://youtube.com/watch?v=VIDEO_ID"

# Plain text (good for piping into further processing)
python3 SKILL_DIR/scripts/fetch_transcript.py "URL" --text-only

# With timestamps
python3 SKILL_DIR/scripts/fetch_transcript.py "URL" --timestamps

# Specific language with fallback chain
python3 SKILL_DIR/scripts/fetch_transcript.py "URL" --language tr,en
```

## Output Formats

After fetching the transcript, format it based on what the user asks for:

- **Chapters**: Group by topic shifts, output timestamped chapter list
- **Summary**: Concise 5-10 sentence overview of the entire video
- **Chapter summaries**: Chapters with a short paragraph summary for each
- **Thread**: Twitter/X thread format — numbered posts, each under 280 chars
- **Blog post**: Full article with title, sections, and key takeaways
- **Quotes**: Notable quotes with timestamps

### Example — Chapters Output

```
00:00 Introduction — host opens with the problem statement
03:45 Background — prior work and why existing solutions fall short
12:20 Core method — walkthrough of the proposed approach
24:10 Results — benchmark comparisons and key takeaways
31:55 Q&A — audience questions on scalability and next steps
```

## Workflow

1. **Fetch** the transcript using the helper script with `--text-only --timestamps`.
2. **Validate**: confirm the output is non-empty and in the expected language. If empty, retry without `--language` to get any available transcript.
3. **If transcripts/captions are disabled, fall back to audio transcription instead of stopping** when the user asked to understand the video:
   ```bash
   mkdir -p /tmp/youtube_<VIDEO_ID>
   python3 -m yt_dlp -f 'bestaudio[ext=m4a]/bestaudio' --no-playlist -o '/tmp/youtube_<VIDEO_ID>/audio.%(ext)s' '<URL>'
   python3 - <<'PY'
   from faster_whisper import WhisperModel
   from pathlib import Path
   audio = '/tmp/youtube_<VIDEO_ID>/audio.m4a'
   model = WhisperModel('base', device='cpu', compute_type='int8')
   segments, info = model.transcribe(audio, language=None, vad_filter=True, beam_size=1)
   out = []
   for s in segments:
       out.append(f"[{int(s.start//60):02d}:{int(s.start%60):02d}] {s.text.strip()}")
   Path('/tmp/youtube_<VIDEO_ID>/transcript.txt').write_text('\n'.join(out), encoding='utf-8')
   print(info.language, info.language_probability)
   print('/tmp/youtube_<VIDEO_ID>/transcript.txt')
   PY
   ```
   If the language is known, pass `language='zh'`, `language='en'`, etc. Mention to the user that timestamps/transcription may be approximate.
4. **Get metadata/title when useful**: browser navigation often reveals title even when extraction returns no transcript; `python3 -m yt_dlp --dump-json --no-playlist '<URL>'` can provide title/channel/duration/upload date.
5. **Chunk if needed**: if the transcript exceeds ~50K characters, split into overlapping chunks (~40K with 2K overlap) and summarize each chunk before merging.
6. **Transform** into the requested output format. If the user did not specify a format, default to a summary.
7. **Verify**: re-read the transformed output to check for coherence, correct timestamps, and completeness before presenting.

## Error Handling

- **Transcript disabled**: do not stop immediately. If `yt-dlp` and `faster-whisper` are available or can be installed safely in the current environment, download audio and transcribe locally, then clearly label it as an approximate Whisper transcript. If local audio transcription is unavailable, tell the user and suggest they check if subtitles are available on the video page.
- **Private/unavailable video**: relay the error and ask the user to verify the URL.
- **No matching language**: retry without `--language` to fetch any available transcript, then note the actual language to the user.
- **Dependency missing**: run `pip install youtube-transcript-api` for transcript extraction. For disabled captions fallback, run `pip install yt-dlp faster-whisper` and retry.
