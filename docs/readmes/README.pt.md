<div align="center">

# 🧪 Growth Lab

<p>Execute operações de produto e ciclos de crescimento em linguagem natural: entenda o produto, encontre demanda real, aja e aprenda com os resultados.</p>

[![GitHub stars](https://img.shields.io/github/stars/tsingyuai/growth-lab?style=for-the-badge&logo=github&color=071a2b)](https://github.com/tsingyuai/growth-lab/stargazers)
[![Código aberto](https://img.shields.io/badge/OPEN_SOURCE-YES-2667FF?style=for-the-badge)](https://github.com/tsingyuai/growth-lab)

[Site](https://growthlab.tsingyuai.com)

[简体中文](../../README.md) · [English](../../README.en.md) · [繁體中文](./README.zh-Hant.md) · [Français](./README.fr.md) · [Español](./README.es.md) · [Русский](./README.ru.md) · [Português](./README.pt.md) · [Deutsch](./README.de.md) · [日本語](./README.ja.md) · [한국어](./README.ko.md) · [Türkçe](./README.tr.md) · [Tiếng Việt](./README.vi.md) · [Polski](./README.pl.md)

</div>

## Por que o Growth Lab

A maioria das ferramentas de crescimento com IA resolve apenas uma parte do problema: redação, pesquisa de concorrentes, publicação ou análise. O contexto do produto se perde entre ferramentas, enquanto decisões importantes ficam espalhadas por painéis, documentos, prompts e transferências manuais.

O Growth Lab organiza o crescimento como um ciclo contínuo de aprendizado:

```text
Entender o produto → Identificar usuários e mercados
→ Pesquisar canais e conteúdo → Formular uma estratégia
→ Criar e distribuir → Observar resultados → Aprender e ajustar
```

O Growth Lab usa Codex e Claude Code como Runtime. A sessão é o plano de controle, Skills contêm os métodos, Clients permitem ações externas e o sistema de arquivos preserva a memória de longo prazo.

## O que torna o Growth Lab diferente

- **Ciclo completo de crescimento:** da compreensão da oportunidade à execução, medição e próxima decisão.
- **Colaboração em linguagem natural:** descreva objetivos, receba o trabalho concluído, dê feedback e continue.
- **Informação, método e execução conectados:** o Agent coleta evidências, aplica um método, age e leva o resultado para o próximo ciclo.
- **Código aberto e dados do usuário:** contexto, dados operacionais, Memory e entregáveis permanecem no seu workspace.

## Como começar

```bash
git clone https://github.com/tsingyuai/growth-lab.git
cd growth-lab
```

Abra o diretório no Codex ou Claude Code e descreva o resultado desejado:

```text
Entenda este produto e execute seu primeiro ciclo de crescimento.
Revise os resultados recentes e execute a próxima ação.
```

O Runtime lê os Models disponíveis, constrói o contexto necessário, chama os Collectors e Executors adequados e registra evidências, resultados e próximos passos. O [onboarding Skill](../../models/onboard-growth-lab/SKILL.md) verifica dependências por linguagem natural.

## Capacidades disponíveis

| Nome | Descrição | Resultado observado |
|---|---|---|
| [Ciclo de crescimento de páginas SEO](../../models/run-seo-page-loop/SKILL.md) | Pesquisa necessidades reais de busca e cria páginas úteis que conduzem ao produto. | Novas páginas indexadas em 1–2 dias; impressões e cliques cresceram 1000% na média de 7 dias. |
| [Ciclo de replicação e revisão do Xiaohongshu](../../models/xhs-replicate/SKILL.md) | Coordena coleta, redação, imagens, renderização, conformidade e revisão dos resultados. | Até 4000+ curtidas/salvamentos e 700+ comentários em uma publicação; publicação manual. |

Os resultados dependem do produto, domínio, demanda, qualidade das páginas, autoridade do site e período observado.

## Licença

O Growth Lab é distribuído sob a [Licença Apache 2.0](../../LICENSE).
