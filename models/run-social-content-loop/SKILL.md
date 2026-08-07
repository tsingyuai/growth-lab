---
name: run-social-content-loop
description: 跨平台内容增长闭环——理解产品，编排小红书、X、TikTok、Instagram 或用户指定研究来源，生成 canonical brief，并为一个或多个目标平台分别产出原生内容包后复盘。用户要求单/多平台调研、针对性生成、跨平台改编或多平台版本时使用。
---

# run-social-content-loop

按 [跨平台编排](references/orchestration.md) 执行。机器契约位于 `schemas/`，所有阶段用 `scripts/validate_orchestration.py` 检查。

修改公开 Schema 时，在仓库外开发 venv 安装 `requirements-dev.txt`，运行 `scripts/test_validate_orchestration.py`；测试必须通过 Draft 2020-12 meta-schema、有效 fixture 和无效 fixture 检查。

## 目标与边界

把产品事实、平台证据和每个目标平台经用户确认的主要参考连接成独立原生内容包。研究来源平台与目标发布平台是两个独立字段；从 X 调研不意味着必须发布到 X，也不得把 X Collector 混入小红书 Collector。

当前发布边界：默认只生成发布包。X 可使用单独配置的官方 API Client；小红书可使用明确标注的 browser-first 发布 Client；微信可使用官方 API Client。所有真实发布仍需当前完整包的逐次授权，浏览器登录或 API 配置不等于发布授权。

在进入研究样本选择后的任何内容生成或转换前，先取得 `content_governance` 明确确认：用户/发布者理解本 Skill 生成、推荐、改写、翻译、渲染或处理的任何内容，在任何阶段和任何情况下都不代表 Skill 的倾向、观点或背书；发布者对内容及其使用后果负责并有权操作目标账号。该限制贯穿草稿、预览、保存、排期、发布和发布后复用，即使最终没有发布也有效。未确认不得进入内容生成。中立性不取消安全、权利、事实、隐私、法律和平台合规门禁。

## 用户必须看到的连续反馈

1. 初次说明能力和只读/发布边界，并请用户提供或确认产品载体、目标平台和目标。
   在将研究用于内容生产前展示并记录全生命周期中立性与发布者责任声明；只做只读采集时可以暂不确认，但不得生成或转换发布内容。
2. 产品读取后反馈已确认事实、仍是假设的部分和拟搜索主题。
3. 采集后展示候选的正文摘要、互动证据、代表图片及干净公开链接，并询问想参考哪一条；图片无法内联时必须给原链接。
4. 用户认为候选都一般时，记录原因并调整查询，不能强迫选择弱候选。
5. 进入首次图片生产决策时先检查生图配置：已有提供商时展示提供商、模型、任务范围、候选数量和付费边界，并优先推荐 API 生图以获得更好效果；尚未配置时主动询问用户是否需要配置。配置已存在也不代表调用授权，取得明确确认后才可调用。
6. 生成后展示最终文案、图片、目标账号/平台、发布设置和仍需人工确认的风险。

## 6 步闭环

### ① 建立产品与任务上下文

先读取根目录 [`DATA.md`](../../DATA.md)，据此确定当前产品工作区，再读取 `workspaces/<product-slug>/SOUL.md` 和该工作区内本 Model 的 Memory。缺少稳定产品事实时调用 [`research-product`](../../collectors/research-product/SKILL.md)，只把可靠增量写入当前产品的 `SOUL.md`。确认：研究来源、是否独立分析或综合、允许学习的维度、目标发布平台、单目标或多目标、受众、目标行动、账号角色、是否保存研究证据、是否下载媒体。

先写 `research-plan.json`，明确独立的 `research.sources` 与 `distribution.targets`。支持单来源/多来源、单目标/多目标和用户指定内容组合。运行 `validate_orchestration.py --stage plan` 后才采集。

### ② 连接与采集

- X 来源：调用 [`x-browser`](../../collectors/x-browser/SKILL.md)，强制先做共享网络预检与登录检查。
- 小红书来源：调用 [`xiaohongshu-mcp`](../../collectors/xiaohongshu-mcp/SKILL.md)。
- TikTok/Instagram 来源：分别调用 [`tiktok-mcp`](../../collectors/tiktok-mcp/SKILL.md) 与 [`instagram-mcp`](../../collectors/instagram-mcp/SKILL.md)；只有真实 adapter 通过就绪门禁后才可执行，`missing-runtime` 时不得伪装成可用。
- 所有海外来源先使用统一 `SOCIAL_PROXY_*` 网络策略；profile 与平台会话仍隔离保存。

产品增长调研统一由 [`research-social-content`](../../collectors/research-social-content/SKILL.md) 编排到对应平台 Collector。查询至少覆盖产品类别、用户问题、替代方案和应用场景。每次只运行一个明确查询；原始证据立即写入 `workspaces/<product-slug>/memory/run-social-content-loop/<run>/research/`，不得进入稳定产品资料。平台字段不同可以归一化到本轮 selection，但不得假造目标平台未提供的指标。

多平台互动量不直接横向比较。`synthesize` 只综合重复出现的需求、结构与语境差异；`independent` 保持各来源洞察分离。用户要求只学习一个平台或一个维度时，其他来源和维度不得进入 brief。

### ③ 筛选高质量候选

先机械去重和排除不相关项，再由 Agent 结合以下维度解释评分：

- 与产品问题和目标受众的相关性；
- 钩子是否清楚，正文是否提供可迁移的信息结构；
- 互动证据与发布时间，避免只看绝对点赞数；
- 图片是否清晰、信息层级是否适合目标平台；
- 来源内容的品牌、版权、人物肖像和不可复制元素；
- 从来源语境迁移到当前产品时会改变什么。

每个目标平台最多选择一个主要内容/视觉学习样本。其他帖子只能作为研究证据，不能混合成视觉提示导致风格污染。多目标可以分别选择不同主参考，但都必须进入同一个来源边界记录。默认迁移抽象结构和信息节奏；当单目标明确选择 `close-replication` 并完成 `replication_policy` 风险确认时，允许 1:1 映射主参考的完整卡序、信息层级、相对布局与节奏，但仍必须替换来源原文、图片、logo、人物、专有 UI 和品牌资产。

### ④ 生成平台内容

先写不可直接发布的 `canonical-brief.json`：只含产品事实、受众、目标、核心信息、来源洞察、不可复制边界和每个目标平台的 message job。它必须引用当前 `research-plan.json` 的 SHA-256。取得 `content_governance` 后运行 `validate_orchestration.py --stage generation`。

随后调用 [`adapt-social-platform`](../../executors/adapt-social-platform/SKILL.md)，从同一 brief 为每个目标独立生成平台原生版本。目标为小红书图文时继续委托 [`xhs-render-cards`](../../executors/xhs-render-cards/SKILL.md)，并在首次图片生产决策时执行生图配置检查：配置可用且用户批准时优先用 API 探索两到三个完整效果方向；未配置时主动询问是否配置以提升视觉效果；用户拒绝或配置不可用后才采用纯确定性方案。目标的 `formats` 显式包含 `video` 时调用可选 [`render-social-video`](../../executors/render-social-video/SKILL.md)：若当前运行已有合格且匹配脚本的卡片包，导入已批准卡片及来源清单后复用；若没有，则把视频脚本交给通用 [`render-social-card-pack`](../../executors/render-social-card-pack/SKILL.md) 生成仅供视频使用的镜头卡片，再生成 `video/video-plan.json`、成片、封面、字幕和 manifest。不要因为内部生成镜头卡片而创建小红书发布包。未声明视频时不得启动生图、FFmpeg 或 TTS。每个平台再由 [`social-content-package`](../../executors/social-content-package/SKILL.md) 整理独立发布包。所有产品声明必须来自已确认事实；外文研究证据保留原文和中文译文。

视频需要配音时，在生成前露出当前引擎、模型和音色。默认本地模型不是强制选择：明确告诉用户可以直接要求 Agent 改用 MeloTTS、Qwen3-TTS、CosyVoice 或自有 WAV；替换模型必须继续遵守独立环境、许可证、硬件提示、模型 revision 和音频哈希记录规则。产品宣传视频不得把同一张抽象生成背景反复套用为主要视觉；优先使用真实产品截图、结果图和操作拆帧，缺少合格证据时先把问题露给用户。

当用户希望提升动态镜头时，可提供“本地确定性”与“Seedance 混合 B-roll”选择。Seedance 是可选付费外部服务：在调用前展示模型 Endpoint、片段数量、时长、分辨率、比例、参考素材远程上传边界和费用不确定性，取得本次精确授权后才允许创建任务。默认 `generate_audio=false`，禁止生成或重绘产品 UI、准确文字、数据和商标；生成片段下载并验证后仍由本地字幕、配音和时间线合成。配置存在不等于调用授权，轮询超时只允许 resume，不得重复创建。

完成后运行 `validate_orchestration.py --stage packages`。同一正文复制到多个平台后只改标签不算平台适配，必须失败并重做。

### ⑤ 审核与发布授权

先展示完整预览。默认 `publish.approved=false`、`auto_publish=false`。

在保存平台草稿、预排期或真实发布前，逐次取得针对最终完整内容的明确声明：用户确认拥有所需内容与素材权利，已完整审阅并知情生成过程，确认目标账号和全部分发/排期设置，授权 Agent 仅按当前版本代理操作，并接受内容、账号与发布后果。把确认时间、最终文案 SHA-256 和覆盖正文、素材、平台、账号及设置的发布包 SHA-256 写入 `content_authorization`；任何修改都会使授权失效。

- 人工发布：生成文案、媒体、设置和操作说明，由用户在平台正常界面发布。
- 自动发布：只有仓库内存在已审计的对应 Client，同时目标账号核对、发布清单批准、完整内容哈希和本次命令确认全部满足时才允许调用；browser-first Client 不得冒充官方 API。
- 登录、采集授权或一句“以后可以发”都不能代替每次最终发布确认。
- 点赞、转发、回复、关注和私信是独立权限，不随发布授权自动开放。

X 正式发布只允许使用 `publish-x-official`，不得用浏览器模拟发帖。视频文件的生成不代表当前 X 视频上传路径已经验收。

### ⑥ 结果回收与复盘

保存发布 URL/截图以及 24h、48h、7d 的真实数据。区分内容质量、账号权重和渠道体量；至少三次共现后才提出方法变更，并先给用户 diff。运行记录写入本 Model Memory，方法改进写回负责的 Model/Collector/Executor。

## Memory

```text
workspaces/<product-slug>/memory/run-social-content-loop/<YYYY-MM-DD-HHMM-topic>/
  context.md
  research-plan.json
  research/
  selection.json
  canonical-brief.json
  packages/
    <platform>/
      copy.md
      source-boundary.md
      publish-manifest.json
      assets/
      video/                 # 仅 targets[].formats 包含 video 时存在
  review/
```

Memory 默认被 Git 忽略。不得保存 Cookie、token、代理凭据、带签名媒体 URL、私信、非公开账号数据或未经用户允许的长期私人测试样本。
