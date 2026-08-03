# Growth Lab local configuration

Growth Lab does not contain or distribute API keys. Keep local credentials in the repository-root `.env.local` or inject them through process environment variables. Both `.env.local` and `.env` are ignored by Git.

## First use

From the repository root:

```powershell
Copy-Item .env.example .env.local
notepad .env.local
```

Only configure the capability you intend to use. The onboarding Skill must report missing configuration before starting a paid or authenticated action, explain the fields below, and let the user configure or skip that capability.

## Xiaohongshu collection

Xiaohongshu collection does not use an API key. It uses the browser-first local service from `xpzouying/xiaohongshu-mcp`, a visible QR login, and login state stored outside this repository.

Configure:

```dotenv
XHS_MCP_ENDPOINT=http://127.0.0.1:18063
XHS_MCP_BINARY=C:\path\to\xiaohongshu-mcp.exe
XHS_MCP_LOGIN_BINARY=C:\path\to\xiaohongshu-login.exe
XHS_MCP_COOKIES_PATH=%USERPROFILE%\.growth-lab\xiaohongshu-mcp\cookies.json
DEFAULT_SAMPLE_LIMIT=25
```

- `XHS_MCP_BINARY`: local read-only service executable built or downloaded from the public `xpzouying/xiaohongshu-mcp` project.
- `XHS_MCP_LOGIN_BINARY`: its visible login executable.
- `XHS_MCP_COOKIES_PATH`: external login-state file; never place it in the repository.
- `DEFAULT_SAMPLE_LIMIT`: first-run default. More can be requested, but 25 is recommended for a useful visual review without an unnecessarily long run.

When login is missing, Growth Lab must explain the read-only boundary and ask before opening the QR-login window. Login authorizes reading public research evidence only, not likes, saves, comments, follows, uploads, or publication.

## AI image generation

AI image generation is optional. Collection, copywriting, review, and deterministic card rendering can proceed without an image API. Configure one provider only when generated effects or layers are needed.

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
