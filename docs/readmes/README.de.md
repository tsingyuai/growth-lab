<div align="center">

# 🧪 Growth Lab

<p>Steuere Produktarbeit und Growth-Loops in natürlicher Sprache: Produkt verstehen, echte Nachfrage erkennen, handeln und aus Ergebnissen lernen.</p>

[![GitHub stars](https://img.shields.io/github/stars/tsingyuai/growth-lab?style=for-the-badge&logo=github&color=071a2b)](https://github.com/tsingyuai/growth-lab/stargazers)
[![Open Source](https://img.shields.io/badge/OPEN_SOURCE-YES-2667FF?style=for-the-badge)](https://github.com/tsingyuai/growth-lab)

[Website](https://growthlab.tsingyuai.com)

[简体中文](../../README.md) · [English](../../README.en.md) · [繁體中文](./README.zh-Hant.md) · [Français](./README.fr.md) · [Español](./README.es.md) · [Русский](./README.ru.md) · [Português](./README.pt.md) · [Deutsch](./README.de.md) · [日本語](./README.ja.md) · [한국어](./README.ko.md) · [Türkçe](./README.tr.md) · [Tiếng Việt](./README.vi.md) · [Polski](./README.pl.md)

</div>

## Warum Growth Lab?

Die meisten KI-Growth-Tools lösen nur einen Teil des Problems: Texte, Wettbewerbsanalyse, Veröffentlichung oder Analytics. Produktkontext geht zwischen Werkzeugen verloren, während wichtige Entscheidungen auf Dashboards, Dokumente, Prompts und manuelle Übergaben verteilt bleiben.

Growth Lab organisiert Wachstum als kontinuierlichen Lernkreislauf:

```text
Produkt verstehen → Nutzer und Märkte identifizieren
→ Kanäle und Inhalte untersuchen → Strategie entwickeln
→ Erstellen und verbreiten → Ergebnisse beobachten → Lernen und anpassen
```

Growth Lab nutzt Codex und Claude Code als Runtime. Die Sitzung ist die Steuerungsebene, Skills enthalten Growth-Methoden, Clients ermöglichen externe Aktionen und das Dateisystem bewahrt das Langzeitgedächtnis.

## Was Growth Lab unterscheidet

- **Vollständiger Growth-Lebenszyklus:** von der Chance über Ausführung und Messung bis zur nächsten Entscheidung.
- **Zusammenarbeit in natürlicher Sprache:** Ziele formulieren, fertige Arbeit erhalten, Feedback geben und fortfahren.
- **Information, Methode und Ausführung verbunden:** Der Agent sammelt Belege, wendet Methoden an, handelt und nutzt Ergebnisse im nächsten Durchlauf.
- **Open Source und nutzereigene Daten:** Produktkontext, Betriebsdaten, Memory und Ergebnisse bleiben im eigenen Workspace.

## Erste Schritte

```bash
git clone https://github.com/tsingyuai/growth-lab.git
cd growth-lab
```

Öffne das Verzeichnis in Codex oder Claude Code und beschreibe dein gewünschtes Ergebnis:

```text
Verstehe dieses Produkt und führe seinen ersten Growth-Loop aus.
Prüfe die letzten Ergebnisse und setze die nächste Growth-Aktion um.
```

Die Runtime liest verfügbare Models, erstellt den nötigen Produkt- und Marktkontext, ruft passende Collectors und Executors auf und speichert Belege, Ergebnisse und nächste Schritte. Der [Onboarding Skill](../../models/onboard-growth-lab/SKILL.md) prüft Abhängigkeiten per natürlicher Sprache.

## Verfügbare Fähigkeiten

| Name | Beschreibung | Beobachtetes Ergebnis |
|---|---|---|
| [SEO Page Growth Loop](../../models/run-seo-page-loop/SKILL.md) | Untersucht reale Suchbedürfnisse und erstellt hilfreiche Seiten, die zum Produkt führen. | Neue Seiten nach 1–2 Tagen indexiert; Impressionen und Klicks stiegen im 7-Tage-Mittel um 1000 %. |
| [Xiaohongshu Replication and Review Loop](../../models/xhs-replicate/SKILL.md) | Koordiniert Sammlung, Text, Bilder, Rendering, Compliance und Ergebnisanalyse. | Bis zu 4.000+ Likes/Speicherungen und 700+ Kommentare pro Beitrag; Veröffentlichung bleibt manuell. |

Ergebnisse hängen von Produkt, Domain, Nachfrage, Seitenqualität, Website-Autorität und Beobachtungszeitraum ab.

## Lizenz

Growth Lab steht unter der [Apache License 2.0](../../LICENSE).
