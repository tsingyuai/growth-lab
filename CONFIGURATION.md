# Growth Lab local configuration

Growth Lab does not contain or distribute API keys. Keep local credentials in the repository-root `.env.local` or inject them through process environment variables. Both `.env.local` and `.env` are ignored by Git.

## Network and proxy preflight

Complete this before configuring a social-platform account. Use direct access when it works. If the user's lawful network environment requires a fixed proxy, configure it locally:

```dotenv
SOCIAL_PROXY_MODE=auto
SOCIAL_PROXY_URL=
SOCIAL_PROXY_BYPASS=127.0.0.1,localhost,::1
```

Supported modes:

- `auto`: test direct access first, then the configured explicit proxy, then the operating-system proxy path; this is the default.
- `direct`: make remote official-API checks without a proxy.
- `system`: use the operating system or standard process proxy settings.
- `explicit`: use a fixed `http://`, `https://`, `socks4://`, or `socks5://` route for the X browser adapter. Official API connectors may support fewer proxy schemes and must report that separately.

`SOCIAL_PROXY_URL` may contain credentials and is therefore a secret. Configure it in `.env.local` or a system secret manager; never paste it into chat, Memory, SOUL, logs, screenshots, or commits. Growth Lab reports only whether it is present.

For browser-independent, domain-specific routing, select `system` and configure the user's existing Windows proxy, PAC file, or proxy-client rule mode. Growth Lab then starts a normal Chrome or Edge window without injecting `--proxy-server`, so rules such as “X/TikTok/Instagram through proxy, other sites direct” remain effective in either browser. Growth Lab does not create or modify OS/PAC rules automatically. `explicit` is a fixed process route, not domain routing.

The approved browser adapter must map the same mode to its browser launch configuration. This repository does not assume that an arbitrary external Client supports the setting. Loopback traffic to `127.0.0.1`, `localhost`, `::1`, local MCP services and browser debugging ports must always bypass the proxy. Growth Lab never discovers, purchases, rotates or changes proxies to evade regional restrictions, rate limits, CAPTCHA, account controls or platform enforcement.

## First use

From the repository root:

```powershell
Copy-Item .env.example .env.local
notepad .env.local
```

Only configure the capability you intend to use. The onboarding Skill must report missing configuration before starting a paid or authenticated action, explain the fields below, and let the user configure or skip that capability.

During first-time Growth Lab configuration, if no image provider is configured, the Agent must explain that an image API is preferred for higher-quality promotional effects and ask whether the user wants to configure one. It must also explain that later successful generation calls may be paid. When the user agrees to configure, it may run:

```powershell
python models\onboard-growth-lab\scripts\open_local_configuration.py
```

This creates `.env.local` from `.env.example` only when missing and opens the local editor without waiting. The user enters the key locally and tells the Agent after saving; the Agent then reruns the redacted configuration check. Before the first provider call in each run, it must separately show the provider/model, scope, output count, and paid boundary and receive explicit approval. Keys must never be pasted into chat or printed by the check.

## Xiaohongshu collection

Xiaohongshu collection does not use an API key. It uses the browser-first local service from `xpzouying/xiaohongshu-mcp`, a visible QR login, and login state stored outside this repository.

Configure:

```dotenv
XHS_MCP_ENDPOINT=http://127.0.0.1:18063
XHS_MCP_BINARY=C:\path\to\xiaohongshu-mcp.exe
XHS_MCP_LOGIN_BINARY=C:\path\to\xiaohongshu-login.exe
XHS_MCP_COOKIES_PATH=%USERPROFILE%\.growth-lab\clients\xiaohongshu-mcp\cookies.json
DEFAULT_SAMPLE_LIMIT=25
```

- `XHS_MCP_BINARY`: local read-only service executable built or downloaded from the public `xpzouying/xiaohongshu-mcp` project.
- `XHS_MCP_LOGIN_BINARY`: its visible login executable.
- `XHS_MCP_COOKIES_PATH`: external login-state file; never place it in the repository.

Without these overrides, Growth Lab automatically discovers the Windows binaries at `%USERPROFILE%\.growth-lab\clients\xiaohongshu-mcp\xiaohongshu-mcp-windows-amd64.exe` and `%USERPROFILE%\.growth-lab\clients\xiaohongshu-mcp\xiaohongshu-login-windows-amd64.exe`. It uses `cookies.json` in the same external Client directory, while also recognizing the legacy `%USERPROFILE%\.xhs-autopilot\xiaohongshu-mcp\cookies.json` location. Explicit process or `.env.local` values still take precedence.
- `DEFAULT_SAMPLE_LIMIT`: first-run default. More can be requested, but 25 is recommended for a useful visual review without an unnecessarily long run.

When login is missing, Growth Lab must explain the read-only boundary and ask before opening the QR-login window. Login authorizes reading public research evidence only, not likes, saves, comments, follows, uploads, or publication.

Use the coordinator as the normal entry point. Add `--allow-visible-login` only after the user agrees to open the QR window:

```powershell
python collectors\xiaohongshu-mcp\scripts\run_xiaohongshu.py "<topic>" `
  --allow-visible-login --limit 25 --cover-pool 25 `
  --out "workspaces\<product-slug>\memory\<model>\<run>\xiaohongshu-search.json"
```

The coordinator reports status every five seconds while browser authentication is being checked, permits one owned-service restart after a cold-start timeout, resumes the original collection after login, and stops its own service after collection. Default limits are 20 seconds for service startup, 45 seconds per authentication check, 180 seconds for visible login, and 180 seconds for collection. Override them only with the bounded `--runtime-*-timeout` options when the requested batch legitimately needs more time.

## X browser-first collection

X uses the repository-local Client and a dedicated Chrome/Edge profile stored outside the repository. Visible login runs in an ordinary detached browser window; Playwright is used only for subsequent read-only collection. It consumes the shared `SOCIAL_PROXY_*` network policy; do not configure a separate X proxy.

```dotenv
X_BROWSER_PYTHON=%USERPROFILE%\.growth-lab\clients\x-browser-venv\Scripts\python.exe
X_BROWSER_PROFILE_DIR=%LOCALAPPDATA%\growth-lab\x\browser-profile
X_BROWSER_CDP_PORT=19222
SOCIAL_BROWSER_FAMILY=auto
# SOCIAL_BROWSER_PATH=C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe
X_CONNECTIVITY_URL=https://x.com/robots.txt
```

- `X_BROWSER_PYTHON` points to the repository-external venv containing the pinned Playwright dependency.
- `X_BROWSER_PROFILE_DIR` stores the user-completed X login outside the repository.
- `X_BROWSER_CDP_PORT` exposes the dedicated browser only on `127.0.0.1` so the read-only collector can attach without closing the window. Local processes with access to CDP can control that dedicated profile; never expose it to LAN/WAN and never use a primary account.
- `SOCIAL_BROWSER_FAMILY` accepts `auto`, `chrome`, or `edge`; `auto` tries Chrome and then Edge.
- `SOCIAL_BROWSER_PATH` optionally points to a non-standard Chrome or Edge executable.
- `X_CONNECTIVITY_URL` is used only for the low-cost preflight.
- `SOCIAL_PROXY_MODE=auto` first tests direct access and then available configured routes. `explicit` routes the dedicated process through the shared fixed HTTP(S)/SOCKS proxy; `system` inherits operating-system/PAC/domain rules in both Chrome and Edge; `direct` forces direct access.

Onboarding must validate the selected route before opening the browser. It must not silently modify Windows proxy, PAC, VPN, TUN, DNS or firewall settings. Before visible login, warn about rate limits, verification, session loss and account restrictions, and require a non-critical test account acknowledgement. X login authorizes read-only public research only—not likes, reposts, replies, follows, messages, uploads or publication.

TUN is an external network transport, not an authentication bypass. When the user's lawful environment already provides TUN routing, keep `SOCIAL_PROXY_MODE=system`; Growth Lab does not enable, disable, or reconfigure TUN. `SOCIAL_PROXY_BYPASS` keeps the loopback CDP endpoint and local adapters outside that route.

Research can run without persistence, or save under the current Product workspace's ignored `memory/run-social-content-loop/` when the user requests it. Media download is opt-in. Official X publishing is a separate Client and authorization path described below.

### X official publishing API

Browser login does not authorize API publishing. To use the separate official X publishing Client, create an X developer app, authorize the target user with the current write/media scopes, and store its user access token locally:

```dotenv
X_USER_ACCESS_TOKEN=
```

Run `executors/publish-x-official/scripts/publish_x.py --check` before use. Media upload, post creation, post deletion and browser draft deletion are separate actions; each requires its own explicit approval. The Client calls only `https://api.x.com` and never displays the token.

## Xiaohongshu publication

The configured `xpzouying/xiaohongshu-mcp` runtime can publish an image note through authorized browser automation. This is not an official Xiaohongshu open API. Read-only login or collection approval is insufficient: the exact title, body, images, tags, visibility and schedule must be included in `publication_sha256`, and the current run needs separate publication approval plus `--confirm-publish`. Failed or ambiguous publication is never retried automatically.

## WeChat Official Account API

Create or select a WeChat Official Account application that has the required material, draft and publication permissions. Store credentials only in `.env.local` or process environment:

```dotenv
WECHAT_APP_ID=
WECHAT_APP_SECRET=
```

Use `executors/publish-wechat-official-account/scripts/wechat_official_api.py --check` for a redacted presence check. Uploading a thumbnail, creating a draft and submitting it for publication are separate commands and approvals. The Client calls only `https://api.weixin.qq.com`; it stores returned non-sensitive media/publish IDs beside the ignored publication package and never stores the access token.

## Optional social video generator

Video generation is loaded only when a target explicitly requests `video`. Its Python packages and FFmpeg binary remain outside the repository:

```powershell
uv venv "$HOME\.growth-lab\clients\social-video-venv" --python 3.11
uv pip install --python "$HOME\.growth-lab\clients\social-video-venv\Scripts\python.exe" `
  -r executors\render-social-video\requirements-video.txt
```

Configure only when the default path is unsuitable:

```dotenv
VIDEO_RENDERER_PYTHON=%USERPROFILE%\.growth-lab\clients\social-video-venv\Scripts\python.exe
VIDEO_FFMPEG_PATH=
SOCIAL_TTS_PYTHON=%USERPROFILE%\.growth-lab\clients\social-tts-venv\Scripts\python.exe
```

An empty `VIDEO_FFMPEG_PATH` lets `imageio-ffmpeg` provide the binary inside the external video venv. The rendered manifest records the exact FFmpeg version. Growth Lab does not vendor or redistribute FFmpeg.

### Optional Remotion renderer

The built-in Pillow/FFmpeg renderer remains the default. For React-driven motion, designed caption choreography or reusable programmatic video scenes, the Agent may recommend the repository-external Remotion renderer described in [`remotion-renderer.md`](executors/render-social-video/references/remotion-renderer.md).

Before the first installation or use, the Agent must show the exact version and the separate [Remotion License](https://github.com/remotion-dev/remotion/blob/main/LICENSE.md), explain the current free/company eligibility boundary and ask the user to confirm that they are eligible for the free license or hold a Company License. Declining leaves the built-in renderer available. A generic request to generate a video is not installation approval.

After confirmation, keep the pinned runtime, lockfile and minimal acknowledgement under `~/.growth-lab/clients/remotion/` or ignored run Memory. Do not add Remotion to Growth Lab's core dependencies, commit `node_modules`, silently upgrade an existing runtime, or copy the user's organization details into Memory. Remotion 4.0.507 does not require a watermark or attribution in the generated video or its publication description. Re-run the gate after a material license change or major-version upgrade.

For optional local Mandarin narration, install the separate Kokoro environment. It is not required for collection, copy, cards, silent video, Windows SAPI, or user-provided audio:

```powershell
uv venv "$HOME\.growth-lab\clients\social-tts-venv" --python 3.11
uv pip install --python "$HOME\.growth-lab\clients\social-tts-venv\Scripts\python.exe" `
  -r executors\render-social-video\requirements-tts-kokoro.txt
```

The supported local preset is `hexgrad/Kokoro-82M-v1.1-zh` at revision `01e7505bd6a7a2ac4975463114c3a7650a9f7218`, with Apache-2.0 weights. Each run records the engine version, exact model revision, voice ID, speed, license, text hash and WAV hash in `tts-manifest.json`; the final video manifest records that manifest's SHA-256.

Before local TTS generation, tell the user which engine and voice will be used. Also tell them they may ask the Agent to replace this layer with MeloTTS, Qwen3-TTS, CosyVoice, or owned WAV files. Such a request authorizes planning the adapter, not silent installation or voice cloning: the Agent must keep the replacement runtime outside the repository, review its code and weight licenses, disclose hardware/time requirements, record exact model provenance, and regenerate audio for review. Windows SAPI and `none` remain available fallbacks. Rendering never authorizes upload or publication.

### Optional Seedance B-roll

Seedance is a paid, optional B-roll provider. The deterministic renderer, cards, screenshots, local TTS and publication packages do not require it. Create an Ark API key and a video-generation model Endpoint in the provider account you control, then configure locally:

```dotenv
ARK_API_KEY=your-local-secret
ARK_BASE_URL=https://ark.cn-beijing.volces.com/api/v3
SEEDANCE_MODEL_ENDPOINT=your-account-video-endpoint-id
```

Do not paste the key into chat. `SEEDANCE_MODEL_ENDPOINT` is deliberately user-configured because model availability, version and region belong to the provider account; Growth Lab does not silently substitute a model. `ARK_BASE_URL` may be changed to the account's documented regional Ark endpoint, but it must be HTTPS and contain no credentials or query parameters.

The request file remains inside ignored run Memory and contains one text prompt plus optional authorized references. A stable public HTTPS reference may use `url`. A temporary or signed URL must never be written to the request file: put it in a process environment variable beginning with `SEEDANCE_INPUT_` and refer to its name with `url_env`.

```json
{
  "schema_version": 1,
  "provider": "seedance-ark",
  "purpose": "b-roll",
  "scene_id": "hero-motion",
  "content": [
    {
      "type": "text",
      "text": "Slow editorial motion of abstract paper layers; no text, logo, UI, data or people."
    },
    {
      "type": "image_url",
      "url_env": "SEEDANCE_INPUT_HERO_FRAME",
      "role": "first_frame"
    }
  ],
  "options": {
    "duration": 5,
    "ratio": "9:16",
    "resolution": "720p",
    "generate_audio": false,
    "return_last_frame": true,
    "watermark": false
  },
  "input_rights_confirmed": true,
  "remote_asset_upload_authorized": true
}
```

Run free local checks first:

```powershell
& $VIDEO_RENDERER_PYTHON executors\render-social-video\scripts\seedance_provider.py check
& $VIDEO_RENDERER_PYTHON executors\render-social-video\scripts\seedance_provider.py inspect `
  --request <video-package>\seedance\hero-motion\seedance-request.json
```

Before `run`, the Agent must show the exact endpoint, clip count, duration, ratio, resolution, remote-input boundary and known/unknown cost, then obtain approval for that paid request. Only then run:

```powershell
& $VIDEO_RENDERER_PYTHON executors\render-social-video\scripts\seedance_provider.py run `
  --request <video-package>\seedance\hero-motion\seedance-request.json `
  --out <video-package>\seedance\hero-motion `
  --confirm-paid-generation --wait-timeout 900 --poll-interval 5
```

The adapter writes task state immediately after creation. If polling times out, use `resume` with the same request and output directory; do not create another task. If the create transport state is ambiguous, `ambiguous-create.json` blocks all automatic retries until the user checks the Ark console. A successful task is downloaded, fully decoded with FFmpeg and recorded in `seedance-manifest.json` without provider URLs.

Remote task cleanup is independent and never deletes local evidence:

```powershell
& $VIDEO_RENDERER_PYTHON executors\render-social-video\scripts\seedance_provider.py delete `
  --out <video-package>\seedance\hero-motion --confirm-delete
```

Reference URLs are sent to the external provider. Uploading a local screenshot, recording or voice file to obtain such a URL is a separate external action and requires explicit user authorization. Do not use Seedance to redraw Product UI, exact copy, code, statistics, logos or citations. Its output may only enter the video plan as validated `generated-broll`; local text, subtitles, selected narration and final assembly remain authoritative.

## TikTok official API

TikTok uses an OAuth access token issued by a TikTok developer app. The current connector only verifies the identity of the account that authorized the app; it does not grant keyword search, arbitrary public-video download, publishing, likes, comments, follows, or messages.

Configure locally:

```dotenv
TIKTOK_ACCESS_TOKEN=your-local-oauth-token
TIKTOK_API_BASE_URL=https://open.tiktokapis.com
```

The app must have the profile permission required by TikTok Display API. Keep the token out of chat, Memory, SOUL, logs, and commits.

TikTok public-content research uses the separate browser-first Collector at `collectors/tiktok-mcp/`. Its normalized local endpoint is:

```dotenv
TIKTOK_MCP_ENDPOINT=http://127.0.0.1:18064
```

The repository does not yet declare an approved TikTok adapter binary. An endpoint value alone is not readiness. A real adapter must have a verified public source and license, remain outside the repository, use a dedicated non-critical account, and pass health, visible login and one minimal non-empty search before collection is reported as ready.

## Instagram official API

Instagram uses an access token issued through a Meta app. The current connector verifies an authorized Instagram account only; available account types and fields depend on the app's Instagram login flow, granted permissions, and review status. It does not provide keyword search or arbitrary post download.

Configure locally:

```dotenv
INSTAGRAM_ACCESS_TOKEN=your-local-access-token
INSTAGRAM_GRAPH_BASE_URL=https://graph.instagram.com
INSTAGRAM_GRAPH_API_VERSION=
INSTAGRAM_USER_ID=me
INSTAGRAM_PROFILE_FIELDS=user_id,username
```

Set `INSTAGRAM_GRAPH_API_VERSION` to the version used by the Meta app when its login flow requires a versioned path. `INSTAGRAM_GRAPH_BASE_URL` and `INSTAGRAM_USER_ID` also allow the Facebook Login variant to be selected without changing connector code. Never paste the token into conversation or commit it.

Instagram public-content research uses `collectors/instagram-mcp/` through:

```dotenv
INSTAGRAM_MCP_ENDPOINT=http://127.0.0.1:18065
```

The repository does not yet declare an approved Instagram adapter binary. Treat an endpoint value or Graph API token as insufficient until a reviewed external adapter passes the same real-read gate described for TikTok.

## AI image generation

AI image generation is optional for using Growth Lab, but it is the preferred path for visually led promotional covers and effect exploration when configured and explicitly approved. During first-time configuration, the Agent must explain that configuring one provider can produce better visual results and ask whether the user wants to configure it. Collection, copywriting, review, and deterministic rendering can still proceed when the user declines.

### OpenAI-compatible image endpoint

Obtain a key from the provider account you control, then configure:

```dotenv
OPENAI_API_KEY=your-local-secret
OPENAI_BASE_URL=https://api.openai.com
OPENAI_IMAGE_MODEL=gpt-image-2
```

`OPENAI_BASE_URL` is optional for the official endpoint. Set it only for a compatible HTTPS endpoint. A base URL with or without a trailing `/v1` is supported.

### Gemini

Obtain a key from Google AI Studio or Google Cloud, then configure:

```dotenv
GEMINI_API_KEY=your-local-secret
GOOGLE_GEMINI_BASE_URL=https://generativelanguage.googleapis.com
```

Before the first paid image call, onboarding must distinguish `configured` from `verified`, explain that validation may incur cost, and ask for approval. It must never print the key.

## Remove configuration

```powershell
Remove-Item -LiteralPath .env.local
Remove-Item -LiteralPath .env
```

Removing these files disables repository-local credentials. It does not revoke keys at the provider or delete the external Xiaohongshu login state; revoke or remove those at their source.

It also does not delete the external X browser profile or change the user's system/explicit proxy. Remove those separately only when the user explicitly wants to discard them.
