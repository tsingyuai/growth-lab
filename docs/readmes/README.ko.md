<div align="center">

# 🧪 Growth Lab

<p>자연어로 제품 운영과 성장 루프를 실행하세요. 제품을 이해하고, 실제 수요를 찾고, 행동한 뒤 결과에서 다음 단계를 학습합니다.</p>

[![GitHub stars](https://img.shields.io/github/stars/tsingyuai/growth-lab?style=for-the-badge&logo=github&color=071a2b)](https://github.com/tsingyuai/growth-lab/stargazers)
[![오픈 소스](https://img.shields.io/badge/OPEN_SOURCE-YES-2667FF?style=for-the-badge)](https://github.com/tsingyuai/growth-lab)

[웹사이트](https://growthlab.tsingyuai.com)

[简体中文](../../README.md) · [English](../../README.en.md) · [繁體中文](./README.zh-Hant.md) · [Français](./README.fr.md) · [Español](./README.es.md) · [Русский](./README.ru.md) · [Português](./README.pt.md) · [Deutsch](./README.de.md) · [日本語](./README.ja.md) · [한국어](./README.ko.md) · [Türkçe](./README.tr.md) · [Tiếng Việt](./README.vi.md) · [Polski](./README.pl.md)

</div>

## Growth Lab을 만드는 이유

대부분의 AI 성장 도구는 카피 작성, 경쟁사 조사, 게시 또는 분석처럼 문제의 일부만 해결합니다. 도구 사이에서 제품 맥락은 반복해서 사라지고 중요한 결정은 대시보드, 문서, 프롬프트와 수동 인수인계에 흩어집니다.

Growth Lab은 성장을 지속적인 학습 루프로 구성합니다.

```text
제품 이해 → 사용자와 시장 식별 → 채널과 콘텐츠 조사
→ 전략 수립 → 제작과 배포 → 실제 결과 관찰 → 학습하고 조정
```

Growth Lab은 Codex와 Claude Code를 Runtime으로 사용합니다. 세션은 제어 영역, Skill은 성장 방법, Client는 외부 실행 능력, 파일 시스템은 장기 기억 역할을 합니다.

## Growth Lab의 차별점

- **완전한 성장 수명주기:** 기회 이해부터 실행, 측정, 다음 의사결정까지 연결합니다.
- **자연어 기반 협업:** 목표를 전달하고, 완료된 작업을 받고, 피드백한 뒤 계속 진행합니다.
- **정보·방법·실행의 연결:** Agent가 근거를 수집하고 방법을 적용해 행동하며 결과를 다음 루프에 반영합니다.
- **오픈 소스와 사용자 소유 데이터:** 제품 맥락, 운영 데이터, Memory와 결과물이 사용자의 워크스페이스에 남습니다.

## 시작하기

```bash
git clone https://github.com/tsingyuai/growth-lab.git
cd growth-lab
```

Codex 또는 Claude Code에서 디렉터리를 열고 원하는 결과를 설명하세요.

```text
이 제품을 이해하고 첫 번째 성장 루프를 실행해 줘.
최근 결과를 검토하고 다음 성장 행동을 실행해 줘.
```

Runtime은 사용 가능한 Model을 읽고 필요한 맥락을 만든 뒤 적절한 Collector와 Executor를 호출하고 근거, 결과물과 다음 행동을 저장합니다. [onboarding Skill](../../models/onboard-growth-lab/SKILL.md)은 자연어로 모든 의존성을 점검합니다.

## 현재 제공되는 기능

| 이름 | 소개 | 관찰된 결과 |
|---|---|---|
| [SEO 페이지 성장 루프](../../models/run-seo-page-loop/SKILL.md) | 실제 검색 수요를 조사하고 문제를 해결하면서 제품으로 연결되는 페이지를 만듭니다. | 새 페이지가 1~2일 내 색인되었고, 7일 평균 기준 노출과 클릭이 각각 1000% 증가했습니다. |
| [샤오홍슈 복제 및 회고 루프](../../models/xhs-replicate/SKILL.md) | 수집, 작성, 이미지, 렌더링, 규정 검사와 결과 회고를 조율합니다. | 게시물 1개에서 최대 좋아요/저장 4000+, 댓글 700+를 기록했으며 게시는 수동입니다. |

결과는 제품, 도메인, 검색 수요, 페이지 품질, 사이트 권위와 관찰 기간에 따라 달라집니다.

## 라이선스

Growth Lab은 [Apache License 2.0](../../LICENSE)으로 공개됩니다.
