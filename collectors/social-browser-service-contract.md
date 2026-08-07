# Local social browser adapter contract

TikTok and Instagram Skills expose the same user workflow through a loopback-only HTTP adapter. The adapter owns platform-specific browser navigation and ephemeral authentication; Growth Lab owns sanitization, downloads, review manifests and Memory output.

## Security

- Listen only on `127.0.0.1`, `localhost`, or `::1` over HTTP.
- Keep browser profiles, cookies and tokens outside the repository.
- Return credentials only as transient `access_ref`; Growth Lab never persists it.
- Stop on CAPTCHA, challenge, rate limit, login loss or platform risk controls.
- Do not implement likes, comments, follows, messages, uploads or publication in this read-only contract.

## Network contract

- Read `SOCIAL_PROXY_MODE` as `direct`, `system`, or `explicit` before browser startup.
- In `explicit` mode, require `SOCIAL_PROXY_URL` and accept only `http://` or `https://` proxy URLs.
- Apply the proxy only to remote platform traffic. Always bypass it for the loopback adapter, MCP transport and Chrome CDP.
- Treat proxy URLs and credentials as secrets; never return them in tool responses or logs.
- Do not rotate proxies, retry through a different egress, or use a proxy to evade CAPTCHA, rate limits, geographic rules or account controls.
- If an external adapter cannot honor this contract, report it as incompatible rather than silently using a different network path.

## Endpoints

`GET /health`

```json
{"success":true,"data":{"status":"healthy"}}
```

`GET /api/v1/login/status`

```json
{"success":true,"data":{"is_logged_in":true}}
```

`POST /api/v1/content/search`

Request:

```json
{"keyword":"research workflow","filters":{},"max_items":25,"max_scrolls":0}
```

Response item:

```json
{
  "content_id":"public-id",
  "public_url":"https://www.tiktok.com/@author/video/public-id",
  "title":"Public caption or title",
  "content_type":"video",
  "author":"Public author name",
  "visible_engagement":{"likes":"1200","comments":"30","shares":"8","views":"50000"},
  "cover_url":"ephemeral HTTPS media URL",
  "access_ref":"ephemeral detail parameter"
}
```

`POST /api/v1/content/detail`

Request:

```json
{"content_id":"public-id","access_ref":"ephemeral","load_comments":false}
```

Response:

```json
{
  "success":true,
  "data":{
    "content":{
      "content_id":"public-id",
      "public_url":"https://www.instagram.com/reel/public-id/",
      "title":"Public caption",
      "description":"Public description",
      "content_type":"reel",
      "author":"Public author",
      "visible_engagement":{"likes":"1200","comments":"30"}
    },
    "media":[
      {"kind":"keyframe","url":"ephemeral HTTPS media URL"},
      {"kind":"video","url":"ephemeral HTTPS media URL"}
    ]
  }
}
```

Every response uses `{"success":false,"error":"..."}` on failure. Risk-control errors must contain a stable marker such as `captcha`, `challenge`, `rate limit`, or `verify` so the caller stops without retrying.
