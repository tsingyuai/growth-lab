<div align="center">

# 🧪 Growth Lab

<p>Ejecuta operaciones de producto y ciclos de crecimiento con lenguaje natural: entiende el producto, descubre demanda real, actúa y aprende de los resultados.</p>

[![GitHub stars](https://img.shields.io/github/stars/tsingyuai/growth-lab?style=for-the-badge&logo=github&color=071a2b)](https://github.com/tsingyuai/growth-lab/stargazers)
[![Código abierto](https://img.shields.io/badge/OPEN_SOURCE-YES-2667FF?style=for-the-badge)](https://github.com/tsingyuai/growth-lab)

[Sitio web](https://growthlab.tsingyuai.com)

[简体中文](../../README.md) · [English](../../README.en.md) · [繁體中文](./README.zh-Hant.md) · [Français](./README.fr.md) · [Español](./README.es.md) · [Русский](./README.ru.md) · [Português](./README.pt.md) · [Deutsch](./README.de.md) · [日本語](./README.ja.md) · [한국어](./README.ko.md) · [Türkçe](./README.tr.md) · [Tiếng Việt](./README.vi.md) · [Polski](./README.pl.md)

</div>

## Por qué Growth Lab

La mayoría de las herramientas de crecimiento con IA resuelven solo una parte: redactan, investigan competidores, publican o muestran analíticas. El contexto del producto se pierde entre herramientas y las decisiones quedan repartidas entre paneles, documentos, prompts y traspasos manuales.

Growth Lab convierte el crecimiento en un ciclo continuo de aprendizaje:

```text
Entender el producto → Identificar usuarios y mercados
→ Investigar canales y contenidos → Formular una estrategia
→ Crear y distribuir → Observar resultados → Aprender y ajustar
```

Growth Lab usa Codex y Claude Code como Runtime. La sesión es el plano de control, los Skills contienen los métodos de crecimiento, los Clients permiten actuar en servicios externos y el sistema de archivos conserva la memoria.

## Qué lo hace diferente

- **Ciclo de crecimiento completo:** desde entender la oportunidad hasta ejecutar, medir y decidir el siguiente paso.
- **Colaboración en lenguaje natural:** plantea objetivos, recibe trabajo terminado, aporta feedback y continúa.
- **Información, método y ejecución conectados:** el Agent reúne evidencia, aplica un método, actúa e incorpora el resultado al siguiente ciclo.
- **Código abierto y datos del usuario:** el contexto, los datos, la Memory y los entregables permanecen en tu espacio de trabajo.

## Cómo empezar

```bash
git clone https://github.com/tsingyuai/growth-lab.git
cd growth-lab
```

Abre el directorio en Codex o Claude Code y describe el resultado que quieres conseguir:

```text
Entiende este producto y ejecuta su primer ciclo de crecimiento.
Revisa los últimos resultados y ejecuta la siguiente acción.
```

El Runtime lee los Models disponibles, crea el contexto necesario, llama a los Collectors y Executors adecuados y guarda evidencia, resultados, entregables y próximos pasos. El [Skill de onboarding](../../models/onboard-growth-lab/SKILL.md) revisa las dependencias mediante lenguaje natural.

## Capacidades disponibles

| Nombre | Descripción | Resultado observado |
|---|---|---|
| [Ciclo de crecimiento de páginas SEO](../../models/run-seo-page-loop/SKILL.md) | Investiga búsquedas reales y crea páginas útiles que resuelven problemas y conducen al producto. | Páginas indexadas en 1–2 días; impresiones y clics aumentaron un 1000 % según la media de 7 días. |
| [Ciclo de réplica y revisión de Xiaohongshu](../../models/xhs-replicate/SKILL.md) | Coordina recopilación, redacción, imágenes, renderizado, cumplimiento y revisión de resultados. | Hasta 4000+ me gusta/guardados y 700+ comentarios en una publicación; la publicación sigue siendo manual. |

Los resultados dependen del producto, dominio, demanda, calidad de las páginas, autoridad del sitio y periodo de observación.

## Licencia

Growth Lab se distribuye bajo la [Licencia Apache 2.0](../../LICENSE).
