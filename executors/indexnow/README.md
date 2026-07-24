# IndexNow executor

向 IndexNow 提交已经上线、更新或删除的 URL。

```bash
export INDEXNOW_KEY='...'
export SITE_URL='https://example.com'

node executors/indexnow/submit-indexnow.mjs \
  https://example.com/new-page
```

站点需要在 `${SITE_URL}/${INDEXNOW_KEY}.txt` 提供纯文本 key 文件。使用其他位置时设置 `INDEXNOW_KEY_LOCATION`。

Client 只从环境变量读取 key，不打印 key、key location 或提交 payload。Agent 应在页面已经部署且公开可访问后调用它。
