<div align="center">

# 🧪 Growth Lab

<p>Ürün operasyonlarını ve büyüme döngülerini doğal dille yürütün: ürünü anlayın, gerçek talebi bulun, harekete geçin ve sonuçlardan öğrenin.</p>

[![GitHub stars](https://img.shields.io/github/stars/tsingyuai/growth-lab?style=for-the-badge&logo=github&color=071a2b)](https://github.com/tsingyuai/growth-lab/stargazers)
[![Açık Kaynak](https://img.shields.io/badge/OPEN_SOURCE-YES-2667FF?style=for-the-badge)](https://github.com/tsingyuai/growth-lab)

[Web sitesi](https://growthlab.tsingyuai.com)

[简体中文](../../README.md) · [English](../../README.en.md) · [繁體中文](./README.zh-Hant.md) · [Français](./README.fr.md) · [Español](./README.es.md) · [Русский](./README.ru.md) · [Português](./README.pt.md) · [Deutsch](./README.de.md) · [日本語](./README.ja.md) · [한국어](./README.ko.md) · [Türkçe](./README.tr.md) · [Tiếng Việt](./README.vi.md) · [Polski](./README.pl.md)

</div>

## Neden Growth Lab?

Çoğu yapay zekâ büyüme aracı sorunun yalnızca bir bölümünü çözer: metin üretir, rakipleri araştırır, içerik yayımlar veya analitik gösterir. Ürün bağlamı araçlar arasında kaybolurken önemli kararlar panolara, belgelere, promptlara ve manuel aktarımlara dağılır.

Growth Lab büyümeyi sürekli bir öğrenme döngüsüne dönüştürür:

```text
Ürünü anla → Kullanıcıları ve pazarları belirle
→ Kanalları ve içeriği araştır → Strateji oluştur
→ Üret ve dağıt → Sonuçları gözlemle → Öğren ve uyarla
```

Growth Lab, Codex ve Claude Code'u Runtime olarak kullanır. Oturum kontrol düzlemidir; Skills büyüme yöntemlerini, Clients dış eylemleri, dosya sistemi ise uzun süreli belleği sağlar.

## Growth Lab'i farklı kılanlar

- **Eksiksiz büyüme yaşam döngüsü:** fırsatı anlamaktan uygulama, ölçüm ve bir sonraki karara kadar.
- **Doğal dille iş birliği:** hedef verin, tamamlanmış işi alın, geri bildirim sağlayın ve devam edin.
- **Bilgi, yöntem ve uygulama bir arada:** Agent kanıt toplar, yöntemi uygular, harekete geçer ve sonucu sonraki döngüye taşır.
- **Açık kaynak ve kullanıcıya ait veriler:** ürün bağlamı, operasyon verileri, Memory ve çıktılar çalışma alanınızda kalır.

## Başlarken

```bash
git clone https://github.com/tsingyuai/growth-lab.git
cd growth-lab
```

Dizini Codex veya Claude Code ile açın ve istediğiniz sonucu açıklayın:

```text
Bu ürünü anla ve ilk büyüme döngüsünü çalıştır.
Son sonuçları değerlendir ve bir sonraki büyüme eylemini uygula.
```

Runtime mevcut Models'ı okur, gerekli bağlamı oluşturur, uygun Collectors ve Executors'ı çağırır; kanıtları, sonuçları ve sonraki adımları kaydeder. [Onboarding Skill](../../models/onboard-growth-lab/SKILL.md) bağımlılıkları doğal dille denetler.

## Mevcut yetenekler

| Ad | Açıklama | Gözlemlenen sonuç |
|---|---|---|
| [SEO Sayfası Büyüme Döngüsü](../../models/run-seo-page-loop/SKILL.md) | Gerçek arama ihtiyaçlarını araştırır ve kullanıcıyı ürüne yönlendiren faydalı sayfalar oluşturur. | Yeni sayfalar 1–2 günde dizine eklendi; 7 günlük ortalamada gösterim ve tıklamalar %1000 arttı. |
| [Xiaohongshu Çoğaltma ve İnceleme Döngüsü](../../models/xhs-replicate/SKILL.md) | Toplama, yazım, görsel, işleme, uyumluluk ve sonuç incelemesini koordine eder. | Tek gönderide 4000+ beğeni/kayıt ve 700+ yorum; yayımlama manuel kalır. |

Sonuçlar ürüne, alan adına, talebe, sayfa kalitesine, site otoritesine ve gözlem aralığına göre değişir.

## Lisans

Growth Lab, [Apache License 2.0](../../LICENSE) ile açık kaynak olarak sunulur.
