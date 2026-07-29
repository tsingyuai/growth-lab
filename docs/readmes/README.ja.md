<div align="center">

# 🧪 Growth Lab

<p>自然言語でプロダクト運用とグロースループを実行します。プロダクトを理解し、実際の需要を見つけ、行動し、結果から次の一手を学びます。</p>

[![GitHub stars](https://img.shields.io/github/stars/tsingyuai/growth-lab?style=for-the-badge&logo=github&color=071a2b)](https://github.com/tsingyuai/growth-lab/stargazers)
[![オープンソース](https://img.shields.io/badge/OPEN_SOURCE-YES-2667FF?style=for-the-badge)](https://github.com/tsingyuai/growth-lab)

[ウェブサイト](https://growthlab.tsingyuai.com)

[简体中文](../../README.md) · [English](../../README.en.md) · [繁體中文](./README.zh-Hant.md) · [Français](./README.fr.md) · [Español](./README.es.md) · [Русский](./README.ru.md) · [Português](./README.pt.md) · [Deutsch](./README.de.md) · [日本語](./README.ja.md) · [한국어](./README.ko.md) · [Türkçe](./README.tr.md) · [Tiếng Việt](./README.vi.md) · [Polski](./README.pl.md)

</div>

## Growth Lab が必要な理由

多くの AI グロースツールは、文章作成、競合調査、投稿、分析など問題の一部分しか解決しません。ツール間でプロダクトの文脈が失われ、重要な判断はダッシュボード、文書、プロンプト、手作業の引き継ぎに分散しています。

Growth Lab はグロースを継続的な学習ループとして構成します。

```text
プロダクトを理解 → ユーザーと市場を特定
→ チャネルとコンテンツを調査 → 戦略を策定
→ 作成と配信 → 結果を観測 → 学習して次の行動を調整
```

Growth Lab は Codex と Claude Code を Runtime として利用します。セッションがコントロールプレーン、Skill がグロース手法、Client が外部アクション、ファイルシステムが長期記憶を担います。

## Growth Lab の特徴

- **グロースの全ライフサイクル：** 機会の理解から実行、測定、次の意思決定までを扱います。
- **自然言語による継続的な協働：** 目標を伝え、完了した成果を受け取り、フィードバックして継続できます。
- **情報・方法・実行を接続：** Agent が証拠を集め、方法を適用し、行動し、その結果を次のループに反映します。
- **オープンソースでデータはユーザー所有：** プロダクト情報、運用データ、Memory、成果物は自分のワークスペースに残ります。

## はじめ方

```bash
git clone https://github.com/tsingyuai/growth-lab.git
cd growth-lab
```

Codex または Claude Code でディレクトリを開き、目的を自然言語で伝えます。

```text
このプロダクトを理解して、最初のグロースループを実行してください。
直近の結果を振り返り、次のグロース施策を実行してください。
```

Runtime は利用可能な Model を読み、必要な文脈を構築し、適切な Collector と Executor を呼び出して、証拠、結果、成果物、次の行動を保存します。[onboarding Skill](../../models/onboard-growth-lab/SKILL.md) により設定依存関係も自然言語で確認できます。

## 利用可能な機能

| 名前 | 概要 | 実測結果 |
|---|---|---|
| [SEO ページグロースループ](../../models/run-seo-page-loop/SKILL.md) | 実際の検索ニーズを調査し、問題を解決しながらプロダクトへ導くページを作成します。 | 新規ページが 1〜2 日でインデックス登録。7 日平均で表示回数とクリック数がそれぞれ 1000% 増加。 |
| [小紅書レプリケーション・レビューループ](../../models/xhs-replicate/SKILL.md) | 収集、執筆、画像生成、レンダリング、コンプライアンス確認、結果分析を連携します。 | 1 投稿で最大 4000+ のいいね／保存、700+ コメント。公開操作は手動です。 |

結果はプロダクト、ドメイン、需要、ページ品質、サイト権威性、観測期間によって異なります。

## ライセンス

Growth Lab は [Apache License 2.0](../../LICENSE) で公開されています。
