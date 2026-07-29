<div align="center">

# 🧪 Growth Lab

<p>Pilotez les opérations produit et les boucles de croissance en langage naturel : comprendre le produit, découvrir la demande réelle, agir, puis apprendre des résultats.</p>

[![GitHub stars](https://img.shields.io/github/stars/tsingyuai/growth-lab?style=for-the-badge&logo=github&color=071a2b)](https://github.com/tsingyuai/growth-lab/stargazers)
[![Open Source](https://img.shields.io/badge/OPEN_SOURCE-YES-2667FF?style=for-the-badge)](https://github.com/tsingyuai/growth-lab)

[Site web](https://growthlab.tsingyuai.com)

[简体中文](../../README.md) · [English](../../README.en.md) · [繁體中文](./README.zh-Hant.md) · [Français](./README.fr.md) · [Español](./README.es.md) · [Русский](./README.ru.md) · [Português](./README.pt.md) · [Deutsch](./README.de.md) · [日本語](./README.ja.md) · [한국어](./README.ko.md) · [Türkçe](./README.tr.md) · [Tiếng Việt](./README.vi.md) · [Polski](./README.pl.md)

</div>

## Pourquoi Growth Lab ?

La plupart des outils de croissance basés sur l’IA ne traitent qu’une partie du problème : rédaction, analyse concurrentielle, publication ou mesure. Le contexte produit se perd entre les outils, tandis que les décisions restent dispersées entre tableaux de bord, documents, prompts et passages de relais manuels.

Growth Lab transforme la croissance en une boucle d’apprentissage continue :

```text
Comprendre le produit → Identifier les utilisateurs et les marchés
→ Étudier les canaux et les contenus → Définir une stratégie
→ Créer et distribuer → Observer les résultats → Apprendre et ajuster
```

Growth Lab utilise Codex et Claude Code comme environnement d’exécution. La session sert de plan de contrôle, les Skills portent les méthodes, les Clients permettent les actions externes et le système de fichiers conserve la mémoire.

## Ce qui le distingue

- **Cycle de croissance complet :** de l’identification d’une opportunité à l’exécution, la mesure et la décision suivante.
- **Collaboration en langage naturel :** donnez un objectif, recevez le travail réalisé, apportez vos retours et poursuivez la boucle.
- **Informations, méthodes et actions réunies :** l’Agent collecte les preuves, applique une méthode, agit et réutilise les résultats.
- **Open source et données sous votre contrôle :** contexte produit, données, Memory et livrables restent dans votre espace de travail.

## Démarrage

```bash
git clone https://github.com/tsingyuai/growth-lab.git
cd growth-lab
```

Ouvrez le dossier dans Codex ou Claude Code et décrivez le résultat attendu :

```text
Comprends ce produit et lance sa première boucle de croissance.
Analyse les derniers résultats puis exécute l’action suivante.
```

Le Runtime lit les Models disponibles, construit le contexte produit et marché nécessaire, appelle les Collectors et Executors appropriés, puis enregistre preuves, résultats, livrables et prochaines actions. Le [Skill d’onboarding](../../models/onboard-growth-lab/SKILL.md) vérifie les dépendances en langage naturel.

## Capacités disponibles

| Nom | Description | Résultat observé |
|---|---|---|
| [Boucle de croissance SEO](../../models/run-seo-page-loop/SKILL.md) | Recherche les besoins exprimés dans les moteurs de recherche et crée des pages utiles qui orientent vers le produit. | Nouvelles pages indexées en 1 à 2 jours ; impressions et clics multipliés par 11 sur une moyenne de 7 jours. |
| [Boucle Xiaohongshu de réplication et d’analyse](../../models/xhs-replicate/SKILL.md) | Coordonne collecte, rédaction, images, rendu, conformité et analyse des résultats. | Jusqu’à 4 000+ mentions J’aime/enregistrements et 700+ commentaires sur une publication ; publication manuelle. |

Les résultats varient selon le produit, le domaine, la demande, la qualité des pages, l’autorité du site et la période observée.

## Licence

Growth Lab est distribué sous [licence Apache 2.0](../../LICENSE).
