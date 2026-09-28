# Xiaohongshu local runtime

Use the local read-only `xiaohongshu-mcp` process for Xiaohongshu research. Keep service binaries and login state outside the repository.

## Configuration ownership

The Growth Lab root `.env.local` and `.env` are local-only and ignored. Precedence is process environment, `.env.local`, then `.env`.

Required for automatic local startup:

- `XHS_MCP_ENDPOINT`: local HTTP endpoint, default `http://127.0.0.1:18063`;
- `XHS_MCP_BINARY`: read-only service executable;
- `XHS_MCP_LOGIN_BINARY`: visible QR-login executable;
- `XHS_MCP_COOKIES_PATH`: external login-state path.

Optional collection controls:

- `XHS_REQUEST_INTERVAL_MS`;
- `XHS_RATE_LIMIT_PER_MIN`;
- `XHS_BACKOFF_SECONDS`;
- `DEFAULT_SAMPLE_LIMIT`, whose recommended value is `25`.

Never import legacy `XHS_COOKIE` into Growth Lab. The MCP browser login owns session state outside the repository.

## Runtime sequence

1. Run the capability check without displaying values.
2. Start the service with `start_xiaohongshu_service.ps1` when the endpoint is unavailable.
3. When login is missing, explain the read-only boundary and ask before opening `login_xiaohongshu.ps1`.
4. Verify login once, collect one 20-30 item batch, and stop on risk or timeout signals without retrying.
5. Store search evidence, visual candidates, and reference selection only in the current Product's ignored social Memory.

Image-generation variables (`OPENAI_API_KEY`, `OPENAI_BASE_URL`, `OPENAI_IMAGE_MODEL`, `GEMINI_API_KEY`, `GOOGLE_GEMINI_BASE_URL`) share the same local configuration boundary. They are read only by the image Executor and capability check.
