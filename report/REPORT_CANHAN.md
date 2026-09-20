# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Trương Hoàng Thành An
**Nhóm:** 4ACE
**Ngày:** 2026-09-20

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**
Độ tương tự cosine cao nghĩa là hai vector embedding có hướng gần nhau, thường biểu diễn hai văn bản có chủ đề hoặc ý nghĩa gần nhau. Giá trị càng gần 1 thì mức tương đồng càng cao.

**Ví dụ có độ tương tự CAO:**

- Câu A: Người mua muốn trả lại sản phẩm bị lỗi.
- Câu B: Khách hàng yêu cầu hoàn hàng vì sản phẩm không hoạt động.
- Tại sao tương đồng: Hai câu diễn đạt cùng ý định dù dùng từ khác nhau.

**Ví dụ có độ tương tự THẤP:**

- Câu A: Người mua yêu cầu hoàn tiền cho đơn hàng bị hư.
- Câu B: Shopee quy định người bán phải đóng gói hàng hóa đúng quy cách.
- Tại sao khác: Một câu nói về quyền lợi hoàn tiền, câu kia nói về nghĩa vụ đóng gói của người bán.

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**
Cosine tập trung vào hướng của vector nên ít bị ảnh hưởng bởi độ dài hoặc độ lớn tuyệt đối của văn bản. Điều này phù hợp với text embedding vì hướng vector thường biểu diễn ý nghĩa tốt hơn độ dài vector.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**

> *Trình bày phép tính:*
> `ceil((10,000 - 50) / (500 - 50)) = ceil(9,950 / 450) = 23` chunks.
> *Đáp án: 23 chunks.*

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**
Số chunk tăng thành `ceil((10,000 - 100) / (500 - 100)) = ceil(24.75) = 25`. Overlap lớn giúp giữ ngữ cảnh ở ranh giới giữa hai chunk, nhưng làm tăng dữ liệu phải embed và có thể tạo nhiều kết quả trùng lặp.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi lập trình (implement) các phần chính trong gói `src`.

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:
Mình dùng regex `(?<=[.!?])\s+` để tách sau dấu chấm, chấm than hoặc chấm hỏi khi sau đó là khoảng trắng hoặc xuống dòng. Các câu được `strip()`, bỏ phần tử rỗng rồi gom tối đa 8 câu vào một chunk; văn bản rỗng trả về `[]` và `max_sentences_per_chunk` tối thiểu là 1. Với corpus Shopee, mình giữ front matter làm metadata, không đưa vào content.

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:
 RecursiveChunker thử các separator theo thứ tự ưu tiên `\n\n`, `\n`, `. `, khoảng trắng rồi mới cắt theo ký tự. Base case là chuỗi rỗng hoặc chuỗi không vượt `chunk_size`; nếu không còn separator, chuỗi dài được cắt thành các đoạn tối đa `chunk_size`.

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:
 Mỗi chunk được lưu cùng `id`, `content`, `metadata` và embedding trong store in-memory. Khi search, query được embedding bằng cùng backend, sau đó tính dot product với từng embedding và sắp xếp score giảm dần trước khi lấy `top_k`.

**`search_with_filter` + `delete_document`** — hướng tiếp cận:
 `search_with_filter` lọc metadata trước rồi mới tính điểm trên tập ứng viên, nên câu hỏi buyer/seller không bị lẫn audience. `delete_document` loại mọi record có `id` hoặc metadata `doc_id` trùng document cần xóa và trả về boolean cho biết có xóa được hay không.

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:
 Agent truy xuất `top_k` chunk bằng `store.search`, nối nội dung thành phần `Context`, rồi đưa context và câu hỏi vào prompt yêu cầu LLM chỉ trả lời dựa trên dữ liệu. Hàm trả về trực tiếp kết quả từ `llm_fn`; benchmark cá nhân tập trung kiểm tra retrieval trước khi đánh giá chất lượng câu trả lời.

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

```
42 passed in 0.07s
```

**Số lượng bài test vượt qua (pass):** 42 / 42

Benchmark riêng của chiến lược SentenceChunker được chạy bằng `python bench_sentence.py` và ghi tại `ket_qua_benchmark_sentence.txt`. Cấu hình: 10 tài liệu, 59 sentence chunks, tối đa 8 câu/chunk; dùng `gemini-embedding-001`, Q1/Q4 lọc `buyer`, Q2/Q3 lọc `seller`, Q5 không lọc.

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

| Cặp | Câu A                                               | Câu B                              | Dự đoán | Điểm thực tế | Đúng? |
| ---- | ---------------------------------------------------- | ----------------------------------- | ---------- | ---------------- | ------- |
| 1    | Người mua đủ điều kiện Trả hàng COM         | Chính sách Trả hàng COM         | cao        | 0.889721         | Có     |
| 2    | Người bán phản hồi yêu cầu trong 2 ngày      | Thời hạn phản hồi seller        | cao        | 0.767599         | Có     |
| 3    | Người bán chịu chi phí trong trường hợp nào | Chi phí hoàn trả seller          | cao        | 0.819656         | Có     |
| 4    | Hoàn phí tự sắp xếp Mall/non-Mall               | Hoàn phí buyer                    | cao        | 0.836462         | Có     |
| 5    | Hoàn tiền ngay tối thiểu 50%                     | Đề xuất hoàn tiền seller/buyer | cao        | 0.744612         | Có     |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**
Kết quả cho thấy embedding Gemini xếp các câu hỏi vào đúng policy buyer/seller khi có metadata filter. Điều bất ngờ là Q5 không filter vẫn lấy hai policy chính ở top-1 và top-2, nhưng cần kiểm tra nội dung từng chunk vì đúng document chưa đồng nghĩa đủ gold answer.

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Chạy **5 câu hỏi đánh giá của nhóm** trên mã nguồn cá nhân của bạn trong gói `src`. **5 câu hỏi này phải trùng với các thành viên cùng nhóm** (xem `REPORT_NHOM.md`).

| # | Câu hỏi (Query)                                                                                                        | Top-1 Chunk truy xuất được (tóm tắt)  | Điểm Score | Có liên quan không? (Relevant)          | Câu trả lời của Agent (tóm tắt)                                          |
| - | ------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------- | ------------ | ------------------------------------------ | ------------------------------------------------------------------------------ |
| 1 | Người mua nào đủ điều kiện Trả hàng COM, hạn mức ShopeeVIP bao nhiêu và trường hợp nào bị loại trừ? | `shopee-chinh-sach-tra-hang-nguoi-mua#6`  | 0.889721     | Có, top-3 cùng đúng policy             | Top-2 chứa điều kiện; top-3 chứa hạn mức/ngoại lệ                     |
| 2 | Người bán phải phản hồi trong bao lâu và điều gì xảy ra nếu trễ?                                           | `shopee-chinh-sach-tra-hang-nguoi-ban#10` | 0.767599     | Có, top-3 cùng seller policy             | Top-1 là section quyền người bán; top-2 liên quan tự động hoàn tiền |
| 3 | Khi nào người bán chịu hoặc không chịu phí hoàn trả?                                                          | `shopee-chinh-sach-tra-hang-nguoi-ban#10` | 0.819656     | Có, mục phí nằm trong top-3            | Top-2 chứa rõ các trường hợp không chịu phí                           |
| 4 | Tự sắp xếp hoàn phí khác nhau thế nào giữa Mall và non-Mall?                                                   | `shopee-chinh-sach-tra-hang-nguoi-mua#11` | 0.836462     | Có một phần                             | Top-1 chứa non-Mall; cần kiểm tra thêm section 8.1 cho Mall                |
| 5 | Hoàn tiền ngay tối thiểu bao nhiêu và buyer làm gì nếu không đồng ý?                                        | `shopee-chinh-sach-tra-hang-nguoi-ban#13` | 0.744612     | Có mức 50%, thiếu lựa chọn đầy đủ | Top-1/top-2 đúng policy nhưng cần ghép với quy trình phản hồi         |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** 5 / 5 ở mức đúng tài liệu; 3 / 5 ở mức có đủ chi tiết gold answer trong top-3.

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**
Qua benchmark, metadata filter giúp loại tài liệu sai audience và làm Q1-Q4 ổn định hơn. Tuy nhiên Q4 và Q5 cho thấy retrieval đúng policy vẫn có thể thiếu một phần đáp án; cần tăng chất lượng chunk hoặc truy xuất nhiều chunk hơn khi câu hỏi yêu cầu so sánh nhiều điều khoản.

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí                                           | Điểm tự đánh giá |
| ---------------------------------------------------- | ---------------------- |
| Khởi động (Warm-up)                               | 5 / 5                    |
| Hướng tiếp cận của tôi (My Approach)           | 10 / 10                   |
| Hoàn thiện code (Core Implementation — tests)     | 30 / 30                   |
| Dự đoán độ tương tự (Similarity Predictions) | 5 / 5                    |
| Kết quả truy xuất của tôi (Competition Results) | 10 / 10                   |
| **Tổng phần cá nhân**                      | **60 / 60**         |
