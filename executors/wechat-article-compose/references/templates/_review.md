# {slug} · 微信公众号发布自检

## 复刻与价值

- 复刻锚：{文章/笔记 URL 或本地路径}；复刻了什么：{结构/节奏/CTA}；渠道调整：{…}
- 价值三问：能提供什么价值 / 解决什么问题 / 为什么现在值得读
- 标题候选（标注钩子类型）：
  1. …

## 基本信息

- [ ] `wechat.yml` 已填写 title / digest / cover（author、content_source_url 可留空用默认值）
- [ ] `article.md` 已定稿
- [ ] 封面图存在且无版权/隐私问题
- [ ] 正文图片均为真实截图或可公开素材，且为本地相对路径

## 合规

- [ ] `check-wechat-compliance.py` 通过
- [ ] `check-banned-phrases.py` 通过
- [ ] 无极限词 / 绝对化承诺 / 无依据结果保证
- [ ] 产品能力与 `SOUL.md` 已验证事实一致
- [ ] `SOUL.md` 中的领域约束已逐条语义审阅
- [ ] AI 生成/辅助内容已按平台规则声明

## 发布

- [ ] `make wechat-preview` 已人工检查
- [ ] 已成功创建微信草稿，并在公众号后台预览
- [ ] `wechat.yml` 中 `publish.approved: true`（仅在决定自动发布时）
- [ ] 环境中 `WECHAT_ENABLE_AUTO_PUBLISH=true`（仅在决定自动发布时）
- [ ] 发布命令显式带 `--confirm-publish`
