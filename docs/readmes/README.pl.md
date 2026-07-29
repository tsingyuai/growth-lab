<div align="center">

# 🧪 Growth Lab

<p>Prowadź operacje produktowe i pętle wzrostu w języku naturalnym: zrozum produkt, odkryj realny popyt, działaj i ucz się z wyników.</p>

[![GitHub stars](https://img.shields.io/github/stars/tsingyuai/growth-lab?style=for-the-badge&logo=github&color=071a2b)](https://github.com/tsingyuai/growth-lab/stargazers)
[![Open Source](https://img.shields.io/badge/OPEN_SOURCE-YES-2667FF?style=for-the-badge)](https://github.com/tsingyuai/growth-lab)

[Strona internetowa](https://growthlab.tsingyuai.com)

[简体中文](../../README.md) · [English](../../README.en.md) · [繁體中文](./README.zh-Hant.md) · [Français](./README.fr.md) · [Español](./README.es.md) · [Русский](./README.ru.md) · [Português](./README.pt.md) · [Deutsch](./README.de.md) · [日本語](./README.ja.md) · [한국어](./README.ko.md) · [Türkçe](./README.tr.md) · [Tiếng Việt](./README.vi.md) · [Polski](./README.pl.md)

</div>

## Dlaczego Growth Lab

Większość narzędzi AI do wzrostu rozwiązuje tylko fragment problemu: tworzy teksty, bada konkurencję, publikuje lub pokazuje analitykę. Kontekst produktu ginie między narzędziami, a decyzje pozostają rozproszone po pulpitach, dokumentach, promptach i ręcznych przekazaniach.

Growth Lab organizuje wzrost jako ciągłą pętlę uczenia się:

```text
Zrozum produkt → Określ użytkowników i rynki
→ Zbadaj kanały i treści → Zbuduj strategię
→ Twórz i dystrybuuj → Obserwuj wyniki → Ucz się i dostosuj
```

Growth Lab używa Codex i Claude Code jako Runtime. Sesja jest płaszczyzną sterowania, Skills zawierają metody wzrostu, Clients umożliwiają działania zewnętrzne, a system plików przechowuje pamięć długoterminową.

## Co wyróżnia Growth Lab

- **Pełny cykl wzrostu:** od zrozumienia szansy przez wykonanie i pomiar po kolejną decyzję.
- **Współpraca w języku naturalnym:** podaj cel, odbierz gotową pracę, przekaż opinię i kontynuuj.
- **Połączone informacje, metody i wykonanie:** Agent zbiera dowody, stosuje metodę, działa i wykorzystuje wynik w następnej pętli.
- **Open source i dane użytkownika:** kontekst produktu, dane operacyjne, Memory i materiały pozostają w Twoim workspace.

## Jak zacząć

```bash
git clone https://github.com/tsingyuai/growth-lab.git
cd growth-lab
```

Otwórz katalog w Codex lub Claude Code i opisz oczekiwany wynik:

```text
Zrozum ten produkt i uruchom jego pierwszą pętlę wzrostu.
Przeanalizuj ostatnie wyniki i wykonaj następne działanie wzrostowe.
```

Runtime czyta dostępne Models, buduje potrzebny kontekst, uruchamia właściwe Collectors i Executors, a następnie zapisuje dowody, wyniki i kolejne kroki. [Onboarding Skill](../../models/onboard-growth-lab/SKILL.md) sprawdza zależności za pomocą języka naturalnego.

## Dostępne możliwości

| Nazwa | Opis | Zaobserwowany wynik |
|---|---|---|
| [Pętla wzrostu stron SEO](../../models/run-seo-page-loop/SKILL.md) | Bada realne potrzeby wyszukiwania i tworzy użyteczne strony prowadzące do produktu. | Nowe strony indeksowane w 1–2 dni; wyświetlenia i kliknięcia wzrosły o 1000% w średniej 7-dniowej. |
| [Pętla replikacji i analizy Xiaohongshu](../../models/xhs-replicate/SKILL.md) | Koordynuje zbieranie, pisanie, obrazy, renderowanie, zgodność i analizę wyników. | Do 4000+ polubień/zapisów i 700+ komentarzy pod jednym postem; publikowanie pozostaje ręczne. |

Wyniki zależą od produktu, domeny, popytu, jakości stron, autorytetu witryny i okresu obserwacji.

## Licencja

Growth Lab jest dostępny na [licencji Apache 2.0](../../LICENSE).
