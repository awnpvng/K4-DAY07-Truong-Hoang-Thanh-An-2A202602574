# Báo Cáo Nhóm — Lab 7: Embedding & Vector Store

**Nhóm:** [4ACE]
**Thành viên:** [Trương Hoàng Thành An, Nguyễn Thị Minh Tiến, Lưu Quang Khải, Phan Thị Khánh Linh]
**Ngày:** 2026-09-20

> **Nộp 1 bản / nhóm.** Phần cá nhân (hướng tiếp cận, kết quả riêng, dự đoán…) mỗi thành viên nộp riêng trong `REPORT_CANHAN.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần nhóm: 40** = Lựa chọn tài liệu (10) + Thiết kế chiến lược (15) + Chất lượng truy xuất (10) + Thuyết trình (5).

---

## 1. Lựa chọn tài liệu (Document Set Quality) — Nhóm (10 điểm)

### Chủ đề (Domain) & Lý Do Chọn

**Chủ đề:** Chính sách đổi trả, hoàn tiền và bảo hành trên Shopee

**Tại sao nhóm chọn chủ đề này?**
Nhóm chọn chủ đề này vì chính sách return-refund có nhiều điều kiện, thời hạn và ngoại lệ phù hợp để đánh giá khả năng truy xuất. Bộ tài liệu cũng có thể phân loại theo đối tượng `buyer` và `seller`, từ đó kiểm tra hiệu quả của metadata filtering. Nhóm chỉ sử dụng các trang chính thức hoặc nguồn công khai có thể kiểm chứng của Shopee.

### Danh sách tài liệu (Data Inventory)

| #  | Tên tài liệu                                                                                                              | Nguồn (Source URL)                            | Ngày lấy / Phiên bản | Số ký tự | Metadata đã gán         |
| -- | ---------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------- | ------------------------ | ----------- | -------------------------- |
| 1  | [shopee-chinh-sach-tra-hang-nguoi-ban.md](../data/return-refund-policy/shopee-chinh-sach-tra-hang-nguoi-ban.md)               | https://help.shopee.vn/portal/4/article/77251  | 2026-09-20 / 2026-03-11  | 23,313      | seller; returns-policy; vi |
| 2  | [shopee-chinh-sach-tra-hang-nguoi-mua.md](../data/return-refund-policy/shopee-chinh-sach-tra-hang-nguoi-mua.md)               | https://help.shopee.vn/portal/4/article/77251  | 2026-09-20 / 2026-03-11  | 22,703      | buyer; returns-policy; vi  |
| 3  | [shopee-huong-dan-chuan-bi-bang-chung.md](../data/return-refund-policy/shopee-huong-dan-chuan-bi-bang-chung.md)               | https://help.shopee.vn/portal/4/article/79467  | 2026-09-20 / v1          | 4,772       | buyer; returns-policy; vi  |
| 4  | [shopee-huong-dan-gui-yeu-cau-tra-hang.md](../data/return-refund-policy/shopee-huong-dan-gui-yeu-cau-tra-hang.md)             | https://help.shopee.vn/portal/4/article/79233  | 2026-09-20 / v1          | 3,477       | buyer; returns-policy; vi  |
| 5  | [shopee-phuong-thuc-va-phi-tra-hang.md](../data/return-refund-policy/shopee-phuong-thuc-va-phi-tra-hang.md)                   | https://help.shopee.vn/portal/4/article/189477 | 2026-09-20 / v1          | 7,987       | buyer; returns-policy; vi  |
| 6  | [shopee-quy-dinh-chung-tra-hang-hoan-tien.md](../data/return-refund-policy/shopee-quy-dinh-chung-tra-hang-hoan-tien.md)       | https://help.shopee.vn/portal/4/article/188931 | 2026-09-20 / v1          | 8,801       | buyer; returns-policy; vi  |
| 7  | [shopee-quy-trinh-xu-ly-tra-hang.md](../data/return-refund-policy/shopee-quy-trinh-xu-ly-tra-hang.md)                         | https://help.shopee.vn/portal/4/article/190242 | 2026-09-20 / v1          | 10,940      | buyer; returns-policy; vi  |
| 8  | [shopee-san-pham-han-che-tra-hang.md](../data/return-refund-policy/shopee-san-pham-han-che-tra-hang.md)                       | https://help.shopee.vn/portal/4/article/79465  | 2026-09-20 / v1          | 2,080       | buyer; returns-policy; vi  |
| 9  | [shopee-thoi-gian-va-cach-kiem-tra-tien-hoan.md](../data/return-refund-policy/shopee-thoi-gian-va-cach-kiem-tra-tien-hoan.md) | https://help.shopee.vn/portal/4/article/189473 | 2026-09-20 / v1          | 5,136       | buyer; returns-policy; vi  |
| 10 | [shopee-tra-hang-doi-y.md](../data/return-refund-policy/shopee-tra-hang-doi-y.md)                                             | https://help.shopee.vn/portal/4/article/204305 | 2026-09-20 / v1          | 9,916       | buyer; returns-policy; vi  |

**Danh sách kiểm tra quản trị dữ liệu (Data governance checklist):**

- [X] Tập tài liệu chỉ chứa nguồn công khai, không chứa dữ liệu cá nhân, thông tin đăng nhập hoặc tài liệu nội bộ.
- [X] Mỗi tài liệu có `source_url`, `retrieved_at`, `document_version` trong metadata.

### Cấu trúc Metadata (Metadata Schema)

| Trường metadata    | Kiểu       | Ví dụ giá trị                                          | Tại sao hữu ích cho truy xuất (retrieval)?      |
| -------------------- | ----------- | ---------------------------------------------------------- | --------------------------------------------------- |
| `doc_id`           | string      | `return-refund-policy`                                   | Xác định tài liệu và hỗ trợ truy vết chunk |
| `title`            | string      | Chính sách đổi trả và hoàn tiền                    | Giúp kiểm tra nguồn nội dung                    |
| `audience`         | enum        | `buyer`, `seller`, `both`                            | Lọc đúng đối tượng hỏi                      |
| `category`         | enum        | `returns-policy`, `refund-policy`, `warranty-policy` | Lọc theo loại chính sách                        |
| `language`         | string      | `vi`                                                     | Phân loại ngôn ngữ                              |
| `source_url`       | string      | URL chính thức của Shopee                               | Truy vết nguồn                                    |
| `retrieved_at`     | date        | `2026-09-20`                                             | Kiểm tra thời điểm thu thập                    |
| `document_version` | string/date | Phiên bản hoặc ngày hiệu lực                         | Phân biệt các bản chính sách                  |

---

## 2. Thiết kế chiến lược (Strategy Design) — Nhóm (15 điểm)

> Mỗi thành viên thử **một chiến lược khác nhau** trên cùng bộ tài liệu; nhóm tổng hợp và so sánh ở đây.

### Phân tích đường cơ sở (Baseline Analysis)

Chạy `ChunkingStrategyComparator().compare()` trên 2-3 tài liệu:

| Tài liệu                               | Chiến lược (Strategy)           | Số lượng Chunk | Độ dài trung bình | Giữ được ngữ cảnh không?                       |
| ---------------------------------------- | ---------------------------------- | ----------------- | --------------------- | ----------------------------------------------------- |
| shopee-chinh-sach-tra-hang-nguoi-mua.md  | FixedSizeChunker (`fixed_size`)  | 34                | 496.6                 | Kích thước ổn định, có thể cắt điều khoản |
| shopee-chinh-sach-tra-hang-nguoi-mua.md  | SentenceChunker (`by_sentences`) | 43                | 390.6                 | Giữ ranh giới câu và số liệu điều khoản      |
| shopee-chinh-sach-tra-hang-nguoi-mua.md  | RecursiveChunker (`recursive`)   | 52                | 322.7                 | Nhiều chunk nhưng giữ cấu trúc mục tốt         |
| shopee-chinh-sach-tra-hang-nguoi-ban.md  | FixedSizeChunker (`fixed_size`)  | 35                | 495.7                 | Kích thước ổn định, có thể cắt điều khoản |
| shopee-chinh-sach-tra-hang-nguoi-ban.md  | SentenceChunker (`by_sentences`) | 43                | 401.4                 | Giữ các nghĩa vụ trong câu/đoạn                |
| shopee-chinh-sach-tra-hang-nguoi-ban.md  | RecursiveChunker (`recursive`)   | 52                | 331.6                 | Giữ cấu trúc mục chi phí và phản hồi          |
| shopee-huong-dan-gui-yeu-cau-tra-hang.md | FixedSizeChunker (`fixed_size`)  | 5                 | 452.4                 | Dễ làm baseline, có thể cắt bước               |
| shopee-huong-dan-gui-yeu-cau-tra-hang.md | SentenceChunker (`by_sentences`) | 7                 | 319.7                 | Giữ từng bước gửi yêu cầu                      |
| shopee-huong-dan-gui-yeu-cau-tra-hang.md | RecursiveChunker (`recursive`)   | 5                 | 450.2                 | Ít chunk, giữ đoạn lớn                           |

Các số liệu được chạy với `chunk_size=500` trên ba tài liệu mới. Tổng corpus hiện có 10 tài liệu, gồm 9 `buyer` và 1 `seller`.

### Chiến lược của từng thành viên

> Mỗi thành viên điền một khối dưới đây (copy thêm nếu nhóm có nhiều hơn 3 người).

**Thành viên 1 — Phan Thị Khánh Linh**

- **Loại chiến lược:** `FixedSizeChunker(chunk_size=500, overlap=50)`.
- **Cách hoạt động:** Mỗi chunk có tối đa 500 ký tự. Chunk kế tiếp bắt đầu sau 450 ký tự, vì vậy 50 ký tự cuối của chunk trước được lặp lại ở chunk sau. Với văn bản ngắn hơn 500 ký tự, hệ thống giữ nguyên thành một chunk.
- **Lý do chọn:** Đây là baseline đơn giản, có số lượng và kích thước chunk dễ kiểm soát. Overlap giúp giữ một phần ngữ cảnh khi điều kiện, thời hạn hoặc ngoại lệ nằm ngay tại ranh giới 500 ký tự; nhờ đó có thể so sánh công bằng với SentenceChunker và RecursiveChunker.
- **Kết quả baseline:** Với ba tài liệu trong bảng baseline, FixedSize tạo lần lượt 12, 7 và 11 chunks; độ dài trung bình lần lượt là 489,4; 451,7; và 488,8 ký tự. Các chunk gần sát giới hạn, nên retrieval tốt với câu hỏi ngắn có từ khóa rõ nhưng có rủi ro tách rời tiêu đề, bảng hoặc một bước trong quy trình.
- **Cách đánh giá:** Chạy cùng 5 benchmark với `top_k=3`; một câu chỉ được tính đúng khi top-3 chứa đủ chunk có số liệu **và** điều kiện áp dụng của gold answer. Đặc biệt kiểm tra câu 3 vì mục “Tự sắp xếp” có nhiều điều kiện dễ bị cắt ở ranh giới chunk.
- **Code sử dụng:**

```python
from src.chunking import FixedSizeChunker

chunker = FixedSizeChunker(chunk_size=500, overlap=50)
chunks = chunker.chunk(document_text)
```

**Thành viên 2 — Trương Hoàng Thành An**

- **Loại chiến lược:** `SentenceChunker(max_sentences_per_chunk=8)`
- **Mô tả & lý do chọn:** Tách theo ranh giới câu rồi gom tối đa 8 câu/chunk, giúp giữ nguyên con số, điều kiện và ngoại lệ trong khi giảm số request embedding API. Chiến lược này phù hợp với hai policy dài vì không cắt giữa câu như fixed-size.
- **Kết quả:** Nạp 59 chunks từ 10 tài liệu; chạy 5 query bằng `gemini-embedding-001`. Q1/Q4 lọc buyer, Q2/Q3 lọc seller, Q5 không filter để kiểm tra khả năng phân biệt hai audience.
- **Code snippet:**

```python
chunker = SentenceChunker(max_sentences_per_chunk=8)
chunks = chunker.chunk(content_without_front_matter)
```

**Thành viên 3 — Nguyen Thi Minh Tien**

- **Loại chiến lược:** `RecursiveChunker(chunk_size=500)`
- **Mô tả & lý do chọn:** Thử separator theo thứ tự đoạn, dòng, câu, từ rồi mới cắt cứng. Cách này phù hợp với policy dài vì ưu tiên giữ paragraph/điều khoản và giảm nguy cơ cắt giữa ý.
- **Kết quả:** 193 chunks, độ dài trung bình 370.6 ký tự, min 117 và max 478 ở `chunk_size=500`; 5/5 gold document nằm trong top-3 trên bộ benchmark cá nhân của Tien.
- **Lưu ý:** Báo cáo Tien dùng bộ query cũ, nên kết quả này là tham khảo về khả năng truy xuất, chưa phải điểm chính thức trên 5 query buyer/seller mới của nhóm.
- **Code snippet:**

```python
chunker = RecursiveChunker(chunk_size=500)
chunks = chunker.chunk(content_without_front_matter)
```

**Thành viên 4 — Lưu Quang Khải**

- **Loại chiến lược:** `HeadingSectionChunker(target_size=800)`
- **Mô tả & lý do chọn:** Tách theo heading Markdown, giữ `section_path`/breadcrumb trong metadata và bảo toàn bảng cùng section. Đây là chiến lược phù hợp nhất với tài liệu chính sách có mục 4, 7, 8, 9 rõ ràng.
- **Kết quả:** 164 chunks với Gemini; cả 5 query mới có chunk liên quan trong top-3, trong đó top-1 thường trỏ đúng section chứa điều khoản.
- **Code snippet:**

```python
chunks = heading_chunker.chunk_document(content, metadata)
```

### So Sánh Giữa Các Thành Viên

| Thành viên              | Chiến lược (Strategy) | Điểm truy xuất (/10) | Điểm mạnh                                                    | Điểm yếu                                                     |
| ------------------------- | ------------------------ | ----------------------- | --------------------------------------------------------------- | --------------------------------------------------------------- |
| Phan Thị Khánh Linh     | FixedSize                | 6/10                    | Baseline đơn giản, dễ kiểm soát overlap                   | Có thể cắt giữa câu/điều khoản                          |
| Trương Hoàng Thành An | Sentence                 | 6/10                    | Giữ ranh giới câu, ít phụ thuộc cấu trúc heading        | Chunk lớn nếu gom nhiều câu; một query cần nhiều section |
| Nguyễn Thị Minh Tiến   | Recursive                | 10/10                   | 193 chunks, cân bằng kích thước và ngữ cảnh             | Có thể tách mất liên kết heading với nội dung           |
| Lưu Quang Khải          | HeadingSection           | 10/10                   | Top-3 chứa đủ chunk liên quan, traceable bằng section_path | Cần parser heading riêng và fallback cho section quá dài   |

**Chiến lược nào tốt nhất cho chủ đề này? Tại sao?**
Với corpus Shopee, HeadingSectionChunker cho kết quả tốt nhất trên bộ 5 query mới vì giữ được ranh giới điều khoản và cung cấp breadcrumb để truy vết. RecursiveChunker là baseline mạnh thứ hai nhờ cân bằng 193 chunks và độ dài trung bình 370.6; SentenceChunker giữ câu tốt nhưng có thể gom quá nhiều nội dung khác section. FixedSize phù hợp làm baseline, nhưng dễ cắt giữa điều kiện và số liệu. Điểm giữa các thành viên chỉ được so sánh chính thức khi mọi người chạy cùng 5 query, cùng embedding Gemini và cùng tiêu chí gold-answer coverage.

---

## 3. Câu hỏi đánh giá & Chất lượng truy xuất (Retrieval Quality) — Nhóm (10 điểm)

### Câu hỏi đánh giá & Câu trả lời chuẩn (nhóm thống nhất)

> **Đúng 5 câu hỏi**, đa dạng, có thể kiểm chứng; **ít nhất 1 câu** cần lọc metadata mới trả lời tốt. Đây là bộ câu hỏi chung cho mọi thành viên chạy.

| # | Câu hỏi (Query)                                                                                                                                                  | Câu trả lời chuẩn (Gold Answer)                                                                                                                                                                                                                                                                                                                                                                                          | Chunk nào chứa thông tin?                                                                                   |
| - | ------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------- |
| 1 | Người mua nào đủ điều kiện Trả hàng COM, hạn mức của ShopeeVIP là bao nhiêu và trường hợp nào bị loại trừ?                                  | Người mua hạng Vàng/Kim Cương hoặc dùng ShopeeVIP đủ điều kiện. ShopeeVIP có hạn mức 15 lần mỗi tháng; hạn mức không cộng dồn, quyền chấm dứt khi gói hết hiệu lực, và không áp dụng cho Shopee Mart hoặc nhóm sản phẩm/người bán bị loại trừ.                                                                                                                                  | [shopee-chinh-sach-tra-hang-nguoi-mua.md](../data/return-refund-policy/shopee-chinh-sach-tra-hang-nguoi-mua.md) |
| 2 | Người bán phải phản hồi yêu cầu Trả hàng/Hoàn tiền trong bao lâu, và điều gì xảy ra nếu không phản hồi đúng hạn?                          | Người bán phải phản hồi trong 02 ngày lịch hoặc thời hạn khác do Shopee quy định. Nếu không phản hồi, Shopee hiểu người bán đồng ý với quyết định xử lý và không khiếu nại; Shopee có thể cân nhắc hoàn tiền mà không cần người mua trả hàng.                                                                                                                                | [shopee-chinh-sach-tra-hang-nguoi-ban.md](../data/return-refund-policy/shopee-chinh-sach-tra-hang-nguoi-ban.md) |
| 3 | Theo chính sách dành cho người bán, trường hợp nào người bán chịu chi phí vận chuyển chiều hoàn trả và trường hợp nào không phải chịu? | Người bán chịu phí với yêu cầu được Shopee chấp thuận không do lỗi người mua/đơn vị vận chuyển, đơn giao không thành công và ngoại lệ do Shopee quy định. Người bán không chịu phí với khiếu nại một phần, chưa nhận hàng, lỗi vận chuyển, hoàn tiền ngay không trả hàng, đơn tự vận chuyển giao không thành công hoặc hình thức người mua tự sắp xếp. | [shopee-chinh-sach-tra-hang-nguoi-ban.md](../data/return-refund-policy/shopee-chinh-sach-tra-hang-nguoi-ban.md) |
| 4 | Nếu người mua tự sắp xếp trả hàng, chính sách hoàn chi phí khác nhau thế nào giữa sản phẩm Shopee Mall và sản phẩm không thuộc Shopee Mall? | Với Shopee Mall, Shopee hoàn đúng số phí vận chuyển đã trả qua Số Dư Tài Khoản Shopee trong 3–5 ngày làm việc khi yêu cầu được chấp nhận. Với sản phẩm không thuộc Shopee Mall, Shopee hỗ trợ một phần bằng Shopee Xu theo chính sách, cũng trong 3–5 ngày làm việc và phải đáp ứng điều kiện hỗ trợ.                                                                   | [shopee-chinh-sach-tra-hang-nguoi-mua.md](../data/return-refund-policy/shopee-chinh-sach-tra-hang-nguoi-mua.md) |
| 5 | Nếu người bán đề xuất Hoàn tiền ngay, mức hoàn tối thiểu là bao nhiêu và người mua có lựa chọn gì nếu không đồng ý?                     | Mức hoàn do hai bên thỏa thuận nhưng không thấp hơn 50% giá trị sản phẩm. Nếu đồng ý, người mua xác nhận để nhận hoàn tiền không cần trả hàng; nếu không đồng ý, người mua có thể tiếp tục trao đổi hoặc chọn trả hàng để yêu cầu hoàn toàn bộ theo quy trình.                                                                                                        | [shopee-chinh-sach-tra-hang-nguoi-mua.md](../data/return-refund-policy/shopee-chinh-sach-tra-hang-nguoi-ban.md) |

Q1 và Q4 dùng `metadata_filter={"audience": "buyer"}`; Q2 và Q3 dùng `metadata_filter={"audience": "seller"}`. Q5 chạy không filter để kiểm tra liệu retrieval có chọn đúng nội dung chung ở hai policy hay bị nhiễu bởi các tài liệu khác. Đây là thiết kế khó hơn vì câu hỏi buộc phân biệt trách nhiệm và quyền lợi của hai audience.

### Tổng hợp chất lượng truy xuất của nhóm

> Cách chấm (theo `docs/SCORING.md`): **2 điểm/câu** — top-3 chứa chunk liên quan + agent trả lời đúng (2), có liên quan nhưng thiếu/không ở top-1 (1), không có trong top-3 (0).

| # | Câu hỏi             | Chiến lược tốt nhất cho câu này | Có chunk liên quan trong top-3?                                             | Ghi chú |
| - | --------------------- | -------------------------------------- | ----------------------------------------------------------------------------- | -------- |
| 1 | HeadingSectionChunker | Có, 2/2 điểm                        | Top-3 chứa điều kiện COM, hạn mức và ngoại lệ theo section 4.2/4.4   |          |
| 2 | HeadingSectionChunker | Có, 2/2 điểm                        | Top-1 chứa section 5 với mốc 02 ngày và hậu quả quá hạn              |          |
| 3 | HeadingSectionChunker | Có, 2/2 điểm                        | Top-1 mục 7.1 và top-2/top-3 mục 7.2 bao phủ hai nhóm trách nhiệm phí |          |
| 4 | HeadingSectionChunker | Có, 2/2 điểm                        | Top-1 mục 8.1 và top-3 mục 8.2 cho phép so sánh Mall/non-Mall            |          |
| 5 | HeadingSectionChunker | Có, 2/2 điểm                        | Top-1 mục 9.5 có ngưỡng 50%, top-3 có quy trình xử lý tiếp theo      |          |

**Lọc bằng metadata có giúp ích không? Ở câu hỏi nào?**
Metadata giúp tạo không gian ứng viên đúng audience: Q1/Q4 chỉ tìm trong policy buyer, Q2/Q3 chỉ tìm trong policy seller. Heading metadata bổ sung thêm lớp lọc/truy vết theo section, nên các câu hỏi cần tổng hợp nhiều mục như Q3-Q5 vẫn lấy được các chunk thuộc đúng điều khoản. Trade-off là heading chunker cần parser riêng và phải có fallback khi một section quá dài.

---

## 4. Thuyết trình (Demo) & Bài học nhóm — Nhóm (5 điểm)

**Những phân tích (insights) hay nhất nhóm sẽ trình bày:**

- HeadingSectionChunker đạt 5/5 câu hỏi mới với Gemini vì section path giữ được quan hệ giữa tiêu đề, điều kiện và số liệu.
- `audience=buyer/seller` loại nhiễu giữa hai policy cùng chủ đề; `section_path` giúp phân biệt các mục chi phí, hạn mức và hoàn tiền.
- SentenceChunker và RecursiveChunker vẫn hữu ích làm baseline, nhưng các query cần ghép nhiều mục có thể cần top-k lớn hơn hoặc heading-aware retrieval.

**Bài học rút ra khi so sánh trong nhóm:**
Việc tách hai policy thành `buyer` và `seller` làm metadata filter có tác dụng thực tế, vì cùng chủ đề nhưng trách nhiệm và thời hạn khác nhau. So sánh bốn chiến lược cho thấy cấu trúc chunk quan trọng không kém embedding: heading path giúp agent truy vết đúng điều khoản, còn recursive/sentence cần dựa nhiều hơn vào top-k.

**Nếu làm lại, nhóm sẽ thay đổi gì trong chiến lược dữ liệu (data strategy)?**
Nếu làm lại, nhóm sẽ giữ hai policy tách audience, bổ sung heading vào metadata của từng chunk và dùng embedding multilingual thật. Nhóm cũng sẽ đánh giá ở mức nội dung gold answer thay vì chỉ kiểm tra `doc_id` đúng.

---

## Tự Đánh Giá (Phần Nhóm)

| Tiêu chí                                   | Điểm tự đánh giá |
| -------------------------------------------- | ---------------------- |
| Lựa chọn tài liệu (Document Set Quality) | 10 / 10                |
| Thiết kế chiến lược (Strategy Design)   | 15 / 15                |
| Chất lượng truy xuất (Retrieval Quality) | 10 / 10                |
| Thuyết trình (Demo)                        | 5 / 5                  |
| **Tổng phần nhóm**                  | **40 / 40**      |
