# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Phan Thị Khánh Linh
**Nhóm:** 4ACE
**Ngày:** 20/9/2026

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**
> Hai vector có hướng gần nhau trong không gian embedding, vì vậy hai đoạn văn bản thường có ý nghĩa hoặc ngữ cảnh tương đồng. Điểm gần 1 biểu thị cùng hướng, điểm gần 0 biểu thị ít liên quan.

**Ví dụ có độ tương tự CAO:**
- Câu A: Người mua có thể trả hàng khi sản phẩm bị lỗi.
- Câu B: Khách hàng được yêu cầu hoàn tiền nếu nhận hàng không đúng/đổi trả vì lỗi.
- Tại sao tương đồng: Cả hai đều mô tả cùng quyền lợi trong chính sách trả hàng/hoàn tiền.

**Ví dụ có độ tương tự THẤP:**
- Câu A: Thời gian bảo hành của sản phẩm là 12 tháng.
- Câu B: Người bán cần cập nhật hình ảnh sản phẩm trước khi đăng bán.
- Tại sao khác: Một câu nói về bảo hành sau mua, câu còn lại nói về thao tác đăng bán.

**Tại sao cosine được ưu tiên hơn khoảng cách Euclid cho text embeddings?**
> Cosine đo góc giữa hai vector, tập trung vào hướng/ngữ nghĩa thay vì độ lớn tuyệt đối. Với embedding văn bản, điều này phù hợp vì các văn bản có thể cùng nghĩa nhưng khác độ dài hoặc chuẩn hoá.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10.000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> Tính theo công thức: `ceil((10000 - 50) / (500 - 50)) = ceil(9950 / 450) = ceil(22.11) = 23`.
> **Đáp án:** 23 chunks.

**Nếu overlap tăng lên 100 thì kết quả thay đổi thế nào?**
> Số chunk là `ceil((10000 - 100) / (500 - 100)) = ceil(9900 / 400) = ceil(24.75) = 25`. Overlap lớn hơn giúp giữ ngữ cảnh ở ranh giới chunk, nhưng tăng số lượng chunk và chi phí lưu trữ/truy xuất.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

### Các hàm chia nhỏ (Chunking Functions)

**`FixedSizeChunker.chunk`**
> Tôi dùng chiến lược này làm baseline: `chunk_size=500`, `overlap=50`. Mỗi chunk không vượt quá 500 ký tự và chunk sau dịch 450 ký tự so với chunk trước. Nếu văn bản ngắn hơn 500 ký tự, trả về một chunk duy nhất. Cách này đơn giản, dễ kiểm soát, nhưng có thể cắt giữa câu/điều kiện dài.

**`SentenceChunker.chunk`**
> Dùng regex tách theo dấu kết thúc câu (`.`, `!`, `?`) và khoảng trắng theo sau, sau đó gom tối đa `max_sentences_per_chunk` câu vào một chunk. Cách này giữ được ranh giới câu tốt hơn, phù hợp với chính sách có nhiều điều kiện và ngoại lệ.

**`RecursiveChunker.chunk` / `_split`**
> Thuật toán ưu tiên chia theo đoạn, dòng, câu, từ, cuối cùng là cắt cứng theo `chunk_size`. Nó giữ cấu trúc tài liệu tốt hơn và giảm mất ngữ cảnh khi có heading hoặc paragraph rõ ràng.

### Lớp EmbeddingStore

**`add_documents` + `search`**
> Mỗi `Document` được lưu dưới dạng record gồm `id`, `content`, `metadata`, và `embedding`. Search tính embedding của câu hỏi, so sánh với các embedding đã lưu và sắp xếp theo score giảm dần.

**`search_with_filter` + `delete_document`**
> Metadata được lọc trước theo tất cả điều kiện key-value, rồi mới thực hiện similarity scoring. Khi xóa tài liệu, hệ thống tìm theo `doc_id` để loại toàn bộ chunk thuộc tài liệu đó.

### Tác tử KnowledgeBaseAgent

**`answer`**
> Agent lấy top-k kết quả, ghép chúng thành context, rồi tạo prompt yêu cầu LLM trả lời chỉ dựa trên context này. Nếu dữ liệu không đủ, nó phải nói rõ là không thể trả lời dựa trên context.

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

### Kết Quả Kiểm Thử (Test Results)

```
C:\Users\DELL\K4-L3B-Phan-Thi-Khanh-Linh-02360> py -3.11 -m pytest tests/ -v
42 passed in 0.09s
```

**Số lượng bài test vượt qua (pass):** **42 / 42**.

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | Hàng lỗi có thể trả hàng không? | Người mua được hoàn tiền nếu nhận hàng lỗi. | cao | ~0.0 với mock | Không |
| 2 | Thời hạn bảo hành là bao lâu? | Thời hạn bảo hành là 12 tháng. | cao | cao | Có |
| 3 | Cách đăng ảnh sản phẩm? | Người bán phải cập nhật ảnh trước khi đăng bán. | cao | thấp | Không |
| 4 | Chính sách hoàn tiền áp dụng khi nào? | Người bán cập nhật ảnh sản phẩm. | thấp | rất thấp | Có |
| 5 | Người mua có thể đổi trả hàng lỗi không? | Thời hạn bảo hành là 12 tháng. | thấp | thấp | Có |

**Kết luận:** mock embedding cho thấy hàm cosine hoạt động đúng nhưng không phản ánh ngữ nghĩa thật; vì vậy, khi cần so sánh chất lượng semantic retrieval, nên dùng embedding model thật như Gemini hoặc Local hơn là mock.

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Tôi đã chạy benchmark thực tế với Gemini embedder trên 5 câu hỏi trong nhóm và thu được các top-1 như sau:

| # | Câu hỏi (Query) | Top-1 Chunk truy xuất được | Score | Có liên quan không? |
|---|-------|-----------------------------|-------|----------------------|
| 1 | Người mua có thể yêu cầu Trả hàng/Hoàn tiền trong những trường hợp nào, và thời hạn gửi yêu cầu là bao lâu? | shopee-chinh-sach-tra-hang-nguoi-mua | 0.7811 | Có |
| 2 | Người mua cần thực hiện những bước nào để gửi yêu cầu trả hàng trực tiếp từ trang đơn hàng? | shopee-huong-dan-gui-yeu-cau-tra-hang | 0.7919 | Có |
| 3 | Nếu chọn “Tự sắp xếp” để trả hàng, người mua phải trả phí và điều kiện để được Shopee hỗ trợ hoàn phí là gì? | shopee-phuong-thuc-va-phi-tra-hang | 0.8031 | Có |
| 4 | Với thẻ tín dụng/ghi nợ, tiền hoàn được trả về đâu và trong bao lâu? | shopee-thoi-gian-va-cach-kiem-tra-tien-hoan | 0.7629 | Có |
| 5 | Khi khiếu nại hàng lỗi, cần chuẩn bị video bằng chứng như thế nào và phải bổ sung trong bao lâu nếu Shopee yêu cầu? | shopee-huong-dan-chuan-bi-bang-chung | 0.8284 | Có |

**Kết luận:** 5/5 câu hỏi đều có top-3 chứa chunk liên quan khi dùng Gemini embedding thật.

**Điều học được:** metadata và chunk structure đóng vai trò rất quan trọng; khi câu hỏi đặc biệt về người mua/người bán, hệ thống cần giữ metadata rõ ràng để tránh lẫn giữa các chính sách liên quan.

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Khởi động (Warm-up) | 5 / 5 |
| Hướng tiếp cận của tôi (My Approach) | 10 / 10 |
| Hoàn thiện code (Core Implementation — tests) | 30 / 30 |
| Dự đoán độ tương tự (Similarity Predictions) | 5 / 5 |
| Kết quả truy xuất của tôi (Competition Results) | 10 / 10 |
| **Tổng phần cá nhân** | **60 / 60** |
