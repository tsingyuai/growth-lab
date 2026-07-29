<div align="center">

# 🧪 Growth Lab

<p>Vận hành sản phẩm và các vòng lặp tăng trưởng bằng ngôn ngữ tự nhiên: hiểu sản phẩm, tìm nhu cầu thật, hành động và học từ kết quả.</p>

[![GitHub stars](https://img.shields.io/github/stars/tsingyuai/growth-lab?style=for-the-badge&logo=github&color=071a2b)](https://github.com/tsingyuai/growth-lab/stargazers)
[![Mã nguồn mở](https://img.shields.io/badge/OPEN_SOURCE-YES-2667FF?style=for-the-badge)](https://github.com/tsingyuai/growth-lab)

[Trang web](https://growthlab.tsingyuai.com)

[简体中文](../../README.md) · [English](../../README.en.md) · [繁體中文](./README.zh-Hant.md) · [Français](./README.fr.md) · [Español](./README.es.md) · [Русский](./README.ru.md) · [Português](./README.pt.md) · [Deutsch](./README.de.md) · [日本語](./README.ja.md) · [한국어](./README.ko.md) · [Türkçe](./README.tr.md) · [Tiếng Việt](./README.vi.md) · [Polski](./README.pl.md)

</div>

## Vì sao có Growth Lab

Phần lớn công cụ tăng trưởng dùng AI chỉ giải quyết một mảnh nhỏ: viết nội dung, nghiên cứu đối thủ, xuất bản hoặc phân tích dữ liệu. Bối cảnh sản phẩm liên tục bị mất giữa các công cụ, còn quyết định quan trọng nằm rải rác trong bảng điều khiển, tài liệu, prompt và các bước bàn giao thủ công.

Growth Lab tổ chức tăng trưởng thành một vòng lặp học hỏi liên tục:

```text
Hiểu sản phẩm → Xác định người dùng và thị trường
→ Nghiên cứu kênh và nội dung → Xây dựng chiến lược
→ Sáng tạo và phân phối → Quan sát kết quả → Học hỏi và điều chỉnh
```

Growth Lab dùng Codex và Claude Code làm Runtime. Phiên làm việc là mặt phẳng điều khiển, Skills chứa phương pháp tăng trưởng, Clients cung cấp khả năng hành động bên ngoài và hệ thống tệp lưu giữ trí nhớ dài hạn.

## Điểm khác biệt

- **Toàn bộ vòng đời tăng trưởng:** từ hiểu cơ hội đến thực thi, đo lường và quyết định bước tiếp theo.
- **Cộng tác bằng ngôn ngữ tự nhiên:** nêu mục tiêu, nhận công việc hoàn chỉnh, phản hồi và tiếp tục.
- **Kết nối thông tin, phương pháp và hành động:** Agent thu thập bằng chứng, áp dụng phương pháp, hành động và đưa kết quả vào vòng lặp sau.
- **Mã nguồn mở, dữ liệu thuộc về người dùng:** bối cảnh sản phẩm, dữ liệu vận hành, Memory và sản phẩm đầu ra nằm trong workspace của bạn.

## Bắt đầu

```bash
git clone https://github.com/tsingyuai/growth-lab.git
cd growth-lab
```

Mở thư mục bằng Codex hoặc Claude Code rồi mô tả kết quả mong muốn:

```text
Hãy hiểu sản phẩm này và chạy vòng lặp tăng trưởng đầu tiên.
Đánh giá kết quả gần nhất rồi thực hiện hành động tăng trưởng tiếp theo.
```

Runtime đọc các Models hiện có, xây dựng bối cảnh cần thiết, gọi Collectors và Executors phù hợp, rồi lưu bằng chứng, kết quả và bước tiếp theo. [Onboarding Skill](../../models/onboard-growth-lab/SKILL.md) kiểm tra các phần phụ thuộc bằng ngôn ngữ tự nhiên.

## Khả năng hiện có

| Tên | Mô tả | Kết quả quan sát được |
|---|---|---|
| [Vòng lặp tăng trưởng trang SEO](../../models/run-seo-page-loop/SKILL.md) | Nghiên cứu nhu cầu tìm kiếm thật và tạo trang hữu ích dẫn người dùng tới sản phẩm. | Trang mới được lập chỉ mục trong 1–2 ngày; lượt hiển thị và nhấp tăng 1000% theo trung bình 7 ngày. |
| [Vòng lặp tái tạo và đánh giá Xiaohongshu](../../models/xhs-replicate/SKILL.md) | Điều phối thu thập, viết, hình ảnh, kết xuất, kiểm tra tuân thủ và đánh giá kết quả. | Một bài đạt tối đa 4000+ lượt thích/lưu và 700+ bình luận; việc đăng bài vẫn do con người thực hiện. |

Kết quả phụ thuộc vào sản phẩm, tên miền, nhu cầu, chất lượng trang, uy tín website và thời gian quan sát.

## Giấy phép

Growth Lab là mã nguồn mở theo [Giấy phép Apache 2.0](../../LICENSE).
