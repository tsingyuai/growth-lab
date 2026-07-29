<div align="center">

# 🧪 Growth Lab

<p>用自然語言運行產品營運與使用者成長閉環：理解產品、發現真實需求、採取行動，再從結果中找到下一步。</p>

[![GitHub stars](https://img.shields.io/github/stars/tsingyuai/growth-lab?style=for-the-badge&logo=github&color=071a2b)](https://github.com/tsingyuai/growth-lab/stargazers)
[![開源](https://img.shields.io/badge/OPEN_SOURCE-YES-2667FF?style=for-the-badge)](https://github.com/tsingyuai/growth-lab)

[官網](https://growthlab.tsingyuai.com)

[简体中文](../../README.md) · [English](../../README.en.md) · [繁體中文](./README.zh-Hant.md) · [Français](./README.fr.md) · [Español](./README.es.md) · [Русский](./README.ru.md) · [Português](./README.pt.md) · [Deutsch](./README.de.md) · [日本語](./README.ja.md) · [한국어](./README.ko.md) · [Türkçe](./README.tr.md) · [Tiếng Việt](./README.vi.md) · [Polski](./README.pl.md)

</div>

## 為什麼做 Growth Lab

大多數 AI 成長工具只解決問題的一個片段：文案、競品研究、內容發布或資料分析。產品脈絡在工具之間反覆遺失，重要決策仍散落在儀表板、文件、Prompt 與人工交接中。

Growth Lab 把成長組織成一個持續學習的閉環：

```text
理解產品 → 判斷使用者與市場 → 研究渠道與內容 → 制定策略
→ 創作與分發 → 收集真實結果 → 學習並調整下一步
```

Growth Lab 以 Codex 和 Claude Code 作為 Runtime。會話是控制面，Skill 提供成長方法，Client 提供外部執行能力，檔案系統則保存長期記憶。

## 有什麼不同

- **完整成長生命週期：** 從理解機會、選擇行動，到執行、衡量與下一輪決策。
- **自然語言協作：** 用對話提出目標、接收成果、提供回饋並繼續執行。
- **資訊、方法與執行相連：** Agent 在同一工作區取得證據、套用方法、完成行動並複盤結果。
- **開源且資料歸使用者：** 產品資料、營運資料、Memory 與產物保留在使用者自己的工作區。

## 如何使用

```bash
git clone https://github.com/tsingyuai/growth-lab.git
cd growth-lab
```

使用 Codex 或 Claude Code 開啟目錄，然後直接描述你想達成的成長結果，例如：

```text
理解這個產品，並運行它的第一個成長閉環。
複盤最近的結果，然後執行下一步成長行動。
```

Runtime 會讀取可用的 Model，建立所需的產品與市場脈絡，呼叫相關 Collector 與 Executor，並把證據、結果、產物與下一步寫回工作區。統一的 [onboarding Skill](../../models/onboard-growth-lab/SKILL.md) 可透過自然語言檢查所有能力所需的設定。

## 現有能力

| 名稱 | 介紹 | 實測結果 |
|---|---|---|
| [SEO 頁面成長閉環](../../models/run-seo-page-loop/SKILL.md) | 研究使用者的真實搜尋需求，建立能解決問題並導向產品的 SEO 頁面。 | 新頁面在 1–2 天內被收錄；按 7 日平均，曝光與點擊均提高 1000%。 |
| [小紅書爆款複刻與複盤閉環](../../models/xhs-replicate/SKILL.md) | 協調採集、創作、圖片生成、卡片渲染、合規檢查與結果複盤。 | 單篇最高獲得 4000+ 讚／收藏與 700+ 留言；發布仍由人工完成。 |

實際結果會受產品、網域、搜尋需求、內容品質、站點權重與觀察時間影響。

## 授權條款

Growth Lab 採用 [Apache License 2.0](../../LICENSE) 開源。
