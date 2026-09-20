# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Nguyen Thi Minh Tien
**Nhóm:** K4-L3B
**MSSV:** 2A202602997
**Ngày:** 2026-09-20

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**
> Độ tương tự cosine đo góc giữa hai vector trong không gian nhiều chiều. Giá trị gần 1 nghĩa là hai văn bản có hướng (ngữ nghĩa) tương tự nhau, bất kể độ dài tuyệt đối.

**Ví dụ có độ tương tự CAO:**
- Câu A: "Tôi muốn trả hàng vì sản phẩm không đúng mô tả"
- Câu B: "Yêu cầu đổi trả vì hàng sai với thông tin đăng bán"
- Tại sao tương đồng: Cả hai đều nói về việc trả hàng do sản phẩm không đúng như mô tả, sử dụng từ khóa chuyên ngành giống nhau.

**Ví dụ có độ tương tự THẤP:**
- Câu A: "Thời gian hoàn tiền qua ví ShopeePay là 24 giờ"
- Câu B: "Cách đóng gói hàng hoàn trả tại bưu cục"
- Tại sao khác: Một câu nói về hoàn tiền, một câu nói về đóng gói — hai chủ đề hoàn toàn khác nhau trong ngữ cảnh trả hàng.

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**
> Cosine similarity chỉ quan tâm đến hướng của vector (ngữ nghĩa), không quan tâm độ dài. Hai câu dài ngắn khác nhau nhưng cùng chủ đề sẽ có cosine cao, trong khi Euclid phạt nặng sự khác biệt về độ dài.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> *Công thức: số_lượng_chunk = ceil((độ_dài - overlap) / (chunk_size - overlap))*
>
> số_lượng_chunk = ceil((10000 - 50) / (500 - 50)) = ceil(9950 / 450) = ceil(22.11) = **23 chunks**

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**
> số_lượng_chunk = ceil((10000 - 100) / (500 - 100)) = ceil(9900 / 400) = ceil(24.75) = **25 chunks**
>
> Tăng overlap lên 100 cho thêm 2 chunks. Overlap cao hơn đảm bảo ngữ cảnh không bị cắt giữa các chunk, đặc biệt quan trọng khi câu hoặc điều khoản bị chia đôi qua hai chunk.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi lập trình (implement) các phần chính trong gói `src`.

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:
> Dùng regex `r'(?<=[.!?])\s+|\.\n'` để tách câu. Regex này phát hiện dấu kết thúc câu (`.`, `!`, `?`) theo sau bởi khoảng trắng, hoặc dấu chấm followed by newline. Sau khi tách, nhóm `max_sentences_per_chunk` câu vào một chunk. Edge case: text ngắn hơn max_sentences trả về 1 chunk duy nhất.

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:
> Thuật toán đệ quy thử các dấu phân cách theo thứ tự ưu tiên: `["\n\n", "\n", ". ", " ", ""]`. Base case: khi text <= chunk_size hoặc hết separators, trả về text như một chunk. Tại mỗi bước: split theo separator hiện tại, nhóm các phần có độ dài <= chunk_size, phần lớn hơn chunk_size được recurse với separator tiếp theo.

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:
> Lưu trữ: Mỗi document được embed thành vector bằng `embedding_fn`, sau đó lưu cùng metadata vào `_store` (in-memory) hoặc ChromaDB (nếu available). Search: Query được embed, sau đó tính cosine similarity với tất cả vectors đã lưu, sort descending theo score, trả về top_k results.

**`search_with_filter` + `delete_document`** — hướng tiếp cận:
> Filter trước: Lọc records theo metadata_filter trước khi tính similarity, giảm không gian tìm kiếm. Delete: Tìm tất cả records có `doc_id` khớp trong metadata, xóa khỏi `_store`, trả về True nếu có record bị xóa.

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:
> Cấu trúc prompt gồm 3 phần: (1) instruction "Dựa trên thông tin sau đây, hãy trả lời câu hỏi", (2) context từ top_k chunks retrieved, (3) câu hỏi. Mỗi chunk được đánh số `[Nguồn N]` để LLM biết nguồn gốc. Nếu không có kết quả, trả lời "Không tìm thấy thông tin liên quan".

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

```
pytest tests/ -v

tests/test_solution.py::TestProjectStructure::test_root_main_entrypoint_exists PASSED
tests/test_solution.py::TestProjectStructure::test_src_package_exists PASSED
tests/test_solution.py::TestClassBasedInterfaces::test_chunker_classes_exist PASSED
tests/test_solution.py::TestClassBasedInterfaces::test_mock_embedder_exists PASSED
tests/test_solution.py::TestFixedSizeChunker::test_returns_list PASSED
tests/test_solution.py::TestFixedSizeChunker::test_single_chunk_if_text_shorter PASSED
tests/test_solution.py::TestFixedSizeChunker::test_chunks_respect_size PASSED
tests/test_solution.py::TestFixedSizeChunker::test_correct_number_of_chunks_no_overlap PASSED
tests/test_solution.py::TestFixedSizeChunker::test_overlap_creates_shared_content PASSED
tests/test_solution.py::TestFixedSizeChunker::test_no_overlap_no_shared_content PASSED
tests/test_solution.py::TestFixedSizeChunker::test_empty_text_returns_empty_list PASSED
tests/test_solution.py::TestSentenceChunker::test_returns_list PASSED
tests/test_solution.py::TestSentenceChunker::test_respects_max_sentences PASSED
tests/test_solution.py::TestSentenceChunker::test_chunks_are_strings PASSED
tests/test_solution.py::TestSentenceChunker::test_single_sentence_max_gives_many_chunks PASSED
tests/test_solution.py::TestRecursiveChunker::test_returns_list PASSED
tests/test_solution.py::TestRecursiveChunker::test_chunks_within_size_when_possible PASSED
tests/test_solution.py::TestRecursiveChunker::test_empty_separators_falls_back_gracefully PASSED
tests/test_solution.py::TestRecursiveChunker::test_handles_double_newline_separator PASSED
tests/test_solution.py::TestEmbeddingStore::test_initial_size_is_zero PASSED
tests/test_solution.py::TestEmbeddingStore::test_add_documents_increases_size PASSED
tests/test_solution.py::TestEmbeddingStore::test_add_more_increases_further PASSED
tests/test_solution.py::TestEmbeddingStore::test_search_returns_list PASSED
tests/test_solution.py::TestEmbeddingStore::test_search_returns_at_most_top_k PASSED
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_content_key PASSED
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_score_key PASSED
tests/test_solution.py::TestEmbeddingStore::test_search_results_sorted_by_score_descending PASSED
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_returns_string PASSED
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_non_empty PASSED
tests/test_solution.py::TestComputeSimilarity::test_identical_vectors_return_1 PASSED
tests/test_solution.py::TestComputeSimilarity::test_orthogonal_vectors_return_0 PASSED
tests/test_solution.py::TestComputeSimilarity::test_zero_vector_returns_0 PASSED
tests/test_solution.py::TestComputeSimilarity::test_opposite_vectors_return_minus_1 PASSED
tests/test_solution.py::TestCompareChunkingStrategies::test_returns_three_strategies PASSED
tests/test_solution.py::TestCompareChunkingStrategies::test_each_strategy_has_count_and_avg_length PASSED
tests/test_solution.py::TestCompareChunkingStrategies::test_counts_are_positive PASSED
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_filter_by_department PASSED
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_no_filter_returns_all_candidates PASSED
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_returns_at_most_top_k PASSED
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_true_for_existing_doc PASSED
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_false_for_nonexistent_doc PASSED
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_reduces_collection_size PASSED

============================== 42 passed in 0.02s ==============================
```

**Số lượng bài test vượt qua (pass):** 42 / 42 ✅

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|------|-------|-------|---------|--------------|-------|
| 1 | "Tôi muốn trả hàng vì đổi ý" | "Sản phẩm còn nguyên tem, nhãn mác, bao bì" | Cao | -0.1145 | Không |
| 2 | "Hoàn tiền qua ví điện tử" | "Thanh toán bằng ShopeePay" | Cao | 0.0016 | Không |
| 3 | "Sản phẩm bị hư hỏng" | "Hàng bể vỡ trong vận chuyển" | Cao | 0.0415 | Không |
| 4 | "Cách đóng gói hàng hoàn trả" | "Thời gian giao hàng nhanh" | Thấp | -0.0719 | Đúng |
| 5 | "Chính sách bảo hành điện tử" | "Món ăn ngon hôm nay" | Thấp | -0.0358 | Đúng |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**
> Bất ngờ nhất: Cặp 1 và 3 có nội dung ngữ nghĩa liên quan nhưng similarity rất thấp. Điều này cho thấy mock embedder (dùng hash MD5) không hiểu ngữ nghĩa mà chỉ dựa trên từ vựng. Với embedder thật (multilingual model), các cặp này sẽ có similarity cao hơn vì cùng topic về "trả hàng" và "hư hỏng/bể vỡ".

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

**Chiến lược chunking của tôi:** RecursiveChunker (chunk_size=500)
**Embedding backend:** Gemini (`gemini-embedding-001`, 3072 dimensions)

### Kết quả Benchmark (5 câu hỏi)

| # | Câu hỏi | Top-1 | Top-2 | Top-3 | Gold in Top-3? |
|---|---------|-------|-------|-------|-----------------|
| 1 | Người mua có thể yêu cầu Trả hàng... | chinh-sach-mua (0.84) | chinh-sach-mua (0.83) | **quy-dinh-chung (0.83)** ⭐ | ✅ |
| 2 | Ai được phép trả hàng do "Đổi ý"? | **tra-hang-doi-y (0.87)** ⭐ | quy-dinh-chung (0.81) | **tra-hang-doi-y (0.80)** ⭐ | ✅ |
| 3 | Sản phẩm nào bị hạn chế? | **san-pham-han-che (0.87)** ⭐ | tra-hang-doi-y (0.82) | tra-hang-doi-y (0.80) | ✅ |
| 4 | Thời gian hoàn tiền ShopeePay? | **thoi-gian-hoan (0.90)** ⭐ | **thoi-gian-hoan (0.83)** ⭐ | **thoi-gian-hoan (0.82)** ⭐ | ✅ |
| 5 | Phí trả hàng tự sắp xếp? | **phuong-thuc-phi (0.78)** ⭐ | chinh-sach-mua (0.76) | **phuong-thuc-phi (0.75)** ⭐ | ✅ |

**Tổng kết: 5/5 gold documents trong Top-3 (100%)**

| Chunk Size | Strategy | Chunks | Avg Length | Min | Max |
|-----------|----------|--------|-----------|-----|-----|
| 200 | FixedSize | 479 | 200.0 | - | - |
| 200 | BySentences | 146 | 488.7 | - | - |
| 200 | Recursive | 513 | 138.4 | - | - |
| 500 | FixedSize | 160 | 499.0 | - | - |
| 500 | BySentences | 146 | 488.7 | - | - |
| 500 | **Recursive** | **193** | **370.6** | 117 | 478 |
| 800 | FixedSize | 76 | 995.3 | - | - |
| 800 | BySentences | 146 | 488.7 | - | - |
| 800 | Recursive | 86 | 834.0 | - | - |

### Chiến lược RecursiveChunking đã chọn

- **chunk_size = 500** — cân bằng giữa số chunks và độ mạch lạc ngữ nghĩa
- **separators**: `["\n\n", "\n", ". ", " ", ""]` — ưu tiên tách theo paragraph trước
- **Kết quả**: 193 chunks, avg 370.6 chars, max 478 chars

### Ưu điểm RecursiveChunking cho Shopee Policy:
1. ✅ Giữ được cấu trúc headings (`##`, `###`) — quan trọng cho policy documents
2. ✅ Tách theo paragraph (`\n\n`) trước — mỗi điều khoản thường là 1 paragraph
3. ✅ Chunks có ngữ nghĩa hoàn chỉnh hơn fixed-size

### Bộ data Shopee (10 documents)

| # | doc_id | audience | title |
|---|--------|---------|-------|
| 1 | shopee-chinh-sach-tra-hang-nguoi-ban | seller | Chính sách Trả hàng và Hoàn tiền — Người Bán |
| 2 | shopee-chinh-sach-tra-hang-nguoi-mua | buyer | Chính sách Trả hàng và Hoàn tiền — Người Mua |
| 3 | shopee-quy-trinh-xu-ly-tra-hang | buyer | Quy trình Shopee xử lý yêu cầu Trả hàng/Hoàn tiền |
| 4 | shopee-tra-hang-doi-y | buyer | Những điều cần biết về Trả hàng do "Đổi ý/không còn nhu cầu" |
| 5 | shopee-quy-dinh-chung-tra-hang-hoan-tien | buyer | Những quy định chung về Trả hàng/Hoàn tiền |
| 6 | shopee-phuong-thuc-va-phi-tra-hang | buyer | Các phương thức gửi hàng hoàn trả và phí hoàn trả |
| 7 | shopee-thoi-gian-va-cach-kiem-tra-tien-hoan | buyer | Thời gian nhận tiền hoàn và cách kiểm tra tiền hoàn |
| 8 | shopee-san-pham-han-che-tra-hang | buyer | Sản phẩm hạn chế trả hàng là gì? |
| 9 | shopee-huong-dan-chuan-bi-bang-chung | buyer | Hướng dẫn chuẩn bị bằng chứng |
| 10 | shopee-huong-dan-gui-yeu-cau-tra-hang | buyer | Hướng dẫn gửi yêu cầu Trả hàng/Hoàn tiền |

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Khởi động (Warm-up) | 5 / 5 |
| Hướng tiếp cận của tôi (My Approach) | 10 / 10 |
| Hoàn thiện code (Core Implementation — tests) | 30 / 30 |
| Dự đoán độ tương tự (Similarity Predictions) | 4 / 5 |
| Kết quả truy xuất của tôi (Competition Results) | 10 / 10 |
| **Tổng phần cá nhân** | **59 / 60** |
