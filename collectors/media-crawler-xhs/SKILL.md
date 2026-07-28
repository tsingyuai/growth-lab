---
name: media-crawler-xhs
description: 使用 MediaCrawler 采集小红书证据，包括关键词搜索、已有笔记链接详情补全、评论、图片或视频以及创作者内容。需要做竞品采样、爆款研究、补全已知链接，或建立可复用候选样本库时使用。包含安全采集方法、溯源要求、通用归一化和写入调用方 Model Memory 的规则。
---

# 小红书采集

先读取并遵循 [media-crawler](../media-crawler/SKILL.md)。本 Skill 统一承担搜索、详情、评论与媒体采集。

## 输入

确认研究目的、关键词或准确链接、目标数量、时间窗、最低互动门槛、是否需要评论/媒体，以及调用方 Model 的 Memory 目录。`xhs-replicate` 默认使用 `memory/xhs-replicate/samples/xhs/<topic>/`。

## 方法

1. 建立 1–3 个意图不同的查询：直接问题、解决方案/品类、用户/场景。不要用近义词堆量。
2. 用 `--platform xhs --type search` 搜索；并发保持 1，先关闭评论与媒体。
3. 搜索结果只作为发现证据。归一化互动数并应用时间窗后排序，不能把搜索摘要当完整正文。
4. 按相关性、互动、形式多样性、时效性和可追溯性选择详情候选，不能只看点赞。调用方研究爆款时，不得仅因候选是商业产品、课程、无源码项目或与当前任务角色不同而剔除；Collector 负责保留证据，是否可迁移及调性差异由调用方 Model 判断。
5. 把带有效 `xsec_token`、通常也带 `xsec_source` 的完整链接写入 `config/xhs_config.py` 的 `XHS_SPECIFIED_NOTE_URL_LIST`，再运行 `--type detail`。
6. 只对 shortlist 开启评论。明确需要素材时才开启上游拼写 `ENABLE_GET_MEIDAS`，并验证下载文件与笔记对应。
7. 创作者研究使用 `XHS_CREATOR_ID_LIST` 和 `--type creator`。
8. 把原始详情、评论、媒体和运行清单复制到 Memory，再运行 `scripts/normalize.py` 生成通用索引。
9. Model 需要长期候选样本库时，传入 `--library-root memory/<model>/libraries/xhs`。派生条目保留人工策展和产品能力证据引用，但不假设任何产品 schema。

```bash
cd "${MEDIACRAWLER_DIR:-${GROWTHLAB_CLIENT_ROOT:-$HOME/.growth-lab/clients}/MediaCrawler}"
uv run main.py --platform xhs --lt qrcode --type search
uv run main.py --platform xhs --lt qrcode --type detail
uv run main.py --platform xhs --lt qrcode --type creator

cd "$REPO_ROOT/growth-lab"
python3 collectors/media-crawler-xhs/scripts/normalize.py \
  --library-root memory/xhs-replicate/libraries/xhs \
  --all memory/xhs-replicate/samples/xhs
```

## 质量检查

- 按 note ID/规范 URL 去重，并保留查询到笔记的来源关系。
- 有什么就记录什么：作者、时间、标题/正文、互动、类型、规范 URL、媒体列表和评论状态。
- 正文、评论或媒体缺失时明确标注，禁止补造。
- 单条成功不等于完整采集；报告截断、风控、删除/私密笔记、过期 token 和媒体失败。
- 登录失效或出现验证时立即停止，不绕过平台控制。

## 交付

返回原始与归一化路径、查询集合、候选与 shortlist 数量、详情成功数、评论/媒体覆盖、采集时间、上游 commit、候选库路径和选择依据。
