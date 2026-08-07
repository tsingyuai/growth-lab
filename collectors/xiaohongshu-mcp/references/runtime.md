# Xiaohongshu local runtime

Use the local read-only `xiaohongshu-mcp` process for Xiaohongshu research. Keep service binaries and login state outside the repository.

## Configuration ownership

The Growth Lab root `.env.local` and `.env` are local-only and ignored. Precedence is process environment, `.env.local`, then `.env`.

Required for automatic local startup:

- `XHS_MCP_ENDPOINT`: local HTTP endpoint, default `http://127.0.0.1:18063`;
- `XHS_MCP_BINARY`: read-only service executable;
- `XHS_MCP_LOGIN_BINARY`: visible QR-login executable;
- `XHS_MCP_COOKIES_PATH`: external login-state path.

When these paths are not explicitly configured, discover the two Windows binaries under `%USERPROFILE%\.growth-lab\clients\xiaohongshu-mcp\` and accept an existing legacy login state under `%USERPROFILE%\.xhs-autopilot\xiaohongshu-mcp\cookies.json`. Explicit environment or `.env.local` values take precedence.

Optional collection controls:

- `XHS_REQUEST_INTERVAL_MS`;
- `XHS_RATE_LIMIT_PER_MIN`;
- `XHS_BACKOFF_SECONDS`;
- `DEFAULT_SAMPLE_LIMIT`, whose recommended value is `25`.

Install the contact-sheet dependency into the repository-external orchestration environment:

```powershell
python -m pip install -r collectors/xiaohongshu-mcp/requirements.txt
```

Never import legacy `XHS_COOKIE` into Growth Lab. The MCP browser login owns session state outside the repository.

## Runtime sequence

1. Run the capability check without displaying values.
2. Use `run_xiaohongshu.py` to start the service when the endpoint is unavailable.
3. Allow one bounded restart when the first cold browser login check times out. Never stop a service the coordinator did not start.
4. When login is missing, explain the read-only boundary, obtain permission, and add `--allow-visible-login`. The coordinator opens the visible login program and resumes the original collection after verification.
5. Collect one 20-30 item batch and stop on risk or repeated timeout signals without further retries.
6. Store search evidence, visual candidates, and reference selection only in the current Product's ignored social Memory.

Image-generation variables (`OPENAI_API_KEY`, `OPENAI_BASE_URL`, `OPENAI_IMAGE_MODEL`, `GEMINI_API_KEY`, `GOOGLE_GEMINI_BASE_URL`) share the same local configuration boundary. They are read only by the image Executor and capability check.
