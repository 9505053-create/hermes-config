# Codex Image Prompt Orchestration

Use this reference when Scott asks Hermes to involve Codex in making an image or wants an image posted back to Telegram.

## Durable pattern

Codex CLI is best treated as the **art director / prompt engineer** in this workflow, not as the binary image renderer.

1. Ask Codex for a concise, high-quality English image-generation prompt.
2. Keep the prompt focused on composition, style, subject, aspect ratio, and negative constraints such as `no readable text`, `no logos`, `no watermark`.
3. Save the Codex prompt and raw output when the session has teaching value under:
   - Windows: `C:\Users\chien\_3AI_WorkSpace\temp_agent\YYYYMMDD_HHMM_task_agent_trace\`
   - WSL: `/mnt/c/Users/chien/_3AI_WorkSpace/temp_agent/YYYYMMDD_HHMM_task_agent_trace/`
4. Use the configured image generation backend/tool to render the image.
5. Verify the output visually or with `vision_analyze` before posting.
6. Post to Telegram with `MEDIA:/absolute/path/to/image.png`.

## Prompt skeleton

```text
You are Codex Agent. Do not generate the binary image. Design a high-quality English prompt for an image-generation model.

Goal: <what Scott wants to see>
Aspect ratio: 16:9 landscape
Style: <cinematic / clean UI / premium tech illustration / etc.>
Elements: <central subject, supporting objects, background>
Constraints: no readable text, no logos, no watermark, avoid tiny labels.
Output only the final image prompt, no explanation.
```

## If the image backend is not configured

Do **not** turn this into a durable negative claim that image generation is impossible. Treat it as setup state:
- record the backend error in the trace package;
- either configure the required image backend/API key if Scott asks, or use a deterministic local fallback only for demos;
- clearly tell Scott which part Codex performed (prompt/art direction) and which part Hermes/tooling performed (rendering/posting).

## Teaching trace checklist

For rich sessions, write:
- `02_codex_prompt.md`
- `03_codex_command.txt`
- `04_codex_raw.log`
- `08_hermes_judgment.md`
- `09_final_transcript.md`
- rendered image under `artifacts/`

Always redact API keys, tokens, cookies, passwords, and other secrets before saving raw logs.
