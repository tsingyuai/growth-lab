---
name: social-content-package
description: 把已验证的 canonical brief、目标平台要求和该目标的主要参考整理成单平台原生发布包。用于 X、Instagram、TikTok、邮件等平台版本的人工协作发布准备和授权门禁；多目标时逐平台调用，默认不发布。
---

# Social content publication package

## 输入

- 已通过编排验证的 `canonical-brief.json` 和一个目标平台 direction；
- 已确认产品事实和目标受众；
- 目标平台、账号角色、内容目标；
- 一个经用户确认的主要参考及不可复制边界；
- 已批准使用的产品截图、品牌素材和生成图片。

## 输出

为每个目标平台分别写入调用 Model 的 Memory：

```text
packages/<platform>/copy.md
packages/<platform>/assets/
packages/<platform>/source-boundary.md
packages/<platform>/publish-manifest.json
```

`publish-manifest.json` 至少包含：

```json
{
  "platform": "x",
  "canonical_brief_sha256": "由编排器计算",
  "account": "由用户确认",
  "copy_file": "copy.md",
  "asset_files": [],
  "content_governance": {
    "all_stages_scope_acknowledged": false,
    "skill_neutrality_persistent_acknowledged": false,
    "publisher_responsibility_accepted": false,
    "account_authority_confirmed": false,
    "safety_rules_remain_applicable_acknowledged": false,
    "confirmed_at": null
  },
  "content_authorization": {
    "rights_confirmed": false,
    "final_content_reviewed": false,
    "generation_disclosed": false,
    "proxy_action_authorized": false,
    "target_account_confirmed": false,
    "distribution_settings_reviewed": false,
    "responsibility_accepted": false,
    "skill_neutrality_acknowledged": false,
    "content_sha256": null,
    "package_sha256": null,
    "draft_sha256": null,
    "publication_sha256": null,
    "confirmed_at": null
  },
  "publish": {
    "approved": false,
    "auto_publish": false,
    "confirmed_at": null
  }
}
```

## 规则

- 在研究样本进入内容生产之前，要求实际使用者/发布者确认 `content_governance`：本 Skill 生成、推荐、改写、翻译、排版或处理的任何内容，在研究选择、草稿、预览、渲染、保存、排期、发布和发布后复用等任何阶段、任何情况下都不代表本 Skill 的倾向、观点或背书；发布者对内容及其使用后果负责，并确认有权操作目标账号。未接受时不得使用本 Skill 进行内容生成或转换。
- 只整理一个目标平台的原生版本；多目标时重复调用，每次使用独立目录、文案、素材清单、来源边界和发布授权，不创建跨平台共享的成稿文件。
- 上述中立性与责任边界持续有效，不因内容未发布、由 Agent 生成、用户参与修改、保存为草稿或发布完成而终止。生成内容可以表达用户选择的立场，但该立场只属于用户/发布者，不属于 Skill。
- 中立性不豁免安全、事实、权利、隐私、法律或平台规则。即使用户承担责任，Skill 仍必须拒绝不允许的请求并执行既有合规检查。
- 只迁移参考内容的抽象钩子、信息顺序和节奏，不复制原文或独特视觉资产。
- 明确区分来源证据、产品事实和生成表达。
- 发布前向用户展示最终文案和全部媒体。
- 草稿写入或发布前，要求用户针对最终完整内容明确确认：对文案与素材拥有充分权利或授权；已完整审阅并知情内容如何生成；授权 Agent 仅按该版本代理操作；理解并承担内容、账号与发布后果；理解 Skill 是中立工具，不表达或背书任何立场。
- 把确认绑定到最终文案 SHA-256 和发布包 SHA-256；发布包哈希覆盖正文、素材清单、平台、目标账号、排期和分发设置。任何一项变化都会使旧确认立即失效，必须重新展示并确认。不得把登录、历史同意、主题批准或“以后可以发”当作本次完整授权。
- 没有已审计 Client 时只做人类协作发布。小红书是明确标注的例外：可在单次发布授权后调用本机 `xiaohongshu-mcp`，但它是浏览器自动化而非官方 API，读取登录授权不能替代发布授权。
- 使用官方或已审计的 browser-first Client 时，必须同时满足目标账号核对、清单批准、完整发布哈希和本次明确确认；任何一项缺失都停在草稿状态。
