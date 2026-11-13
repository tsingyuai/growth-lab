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

## Zhihu collection

Zhihu collection uses the official `zhihu-cli` from the [Zhihu Open Platform](https://developer.zhihu.com/docs?key=zhihu_cli). It does not use MediaCrawler, browser cookies, or page scraping.

First check whether the official CLI is already installed:

```bash
python3 models/onboard-growth-lab/scripts/onboard_zhihu.py status
```

If it is missing, the agreed installation command is:

```bash
python3 models/onboard-growth-lab/scripts/onboard_zhihu.py install --yes
```

The installer downloads only from `developer-cdn.zhihu.com`, verifies the official release manifest, artifact size, and SHA-256, then installs under the current user's application data directory. It does not use `sudo` or modify `PATH`.

Optional path overrides:

```dotenv
ZHIHU_CLI_BIN=/absolute/path/to/official/zhihu-cli
ZHIHU_CLI_HOME=/absolute/path/to/zhihu-cli-install-root
```

Leave both empty unless the workspace needs a non-default installation location. `ZHIHU_CLI_BIN` must point to a binary obtained from Zhihu's official CLI release.

Generate an Access Secret at <https://developer.zhihu.com/profile>. Give it to the Agent only in the private conversation; the Agent must pass it to the official binary through standard input with `auth set --secret-stdin`. Do not put the secret in a command-line argument, repository file, Memory, screenshot, or shared transcript.

On desktop systems the official CLI stores the credential in the operating-system keychain. In headless or container environments, the host Secret Store should inject `ZHIHU_ACCESS_SECRET` into the process that runs the CLI. The CLI does not read project `.env` files automatically. If the variable exists and is invalid, the CLI should not silently fall back to another credential.

The preferred local setup path is the no-echo onboarding prompt:

```bash
python3 models/onboard-growth-lab/scripts/onboard_zhihu.py auth
```

`auth status` only checks local configuration. After approval for online verification and possible quota use, complete onboarding with one real query:

```bash
python3 models/onboard-growth-lab/scripts/onboard_zhihu.py verify \
  --query "a real research query" \
  --yes
```

`verify` runs the official online credential check and requires at least one returned content item. Use `--hot` instead when a real query is not available, but still require one returned hot-list item.

Remove the CLI with the official installer's documented rollback or remove the user application-data directory after confirming no other workspace uses it. Remove the credential with the official `auth logout` command or revoke the Access Secret in the Open Platform profile. Removing `.env.local` does not remove an OS-keychain credential.

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
