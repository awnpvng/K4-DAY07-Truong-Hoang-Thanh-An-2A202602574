# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Lưu Quang Khải  
**Nhóm:** 4ACE  
**Vai trò & Chiến lược:** Thành viên 4 — `HeadingSectionChunker` & Gemini Embedding (`gemini-embedding-001`)  
**Ngày:** 2026-09-20  

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**
> Độ tương tự Cosine đo góc giữa hai vector biểu diễn văn bản trong không gian đa chiều, nhận giá trị từ -1 đến 1 (với text embedding thường từ 0 đến 1). Giá trị càng gần 1 thể hiện hai đoạn văn bản có sự đồng nhất cao về mặt ngữ nghĩa và hướng biểu diễn chủ đề, không phụ thuộc vào độ dài hay số lượng từ của văn bản.

**Ví dụ có độ tương tự CAO:**
- **Câu A:** Chính sách đổi trả hàng áp dụng cho người mua trên Shopee.
- **Câu B:** Khách hàng mua sắm trên Shopee được quyền hoàn trả sản phẩm theo quy định.
- **Tại sao tương đồng:** Cùng diễn đạt quyền lợi hoàn trả sản phẩm của khách hàng trên nền tảng Shopee, dù sử dụng từ vựng khác nhau ("người mua" vs "khách hàng mua sắm", "đổi trả hàng" vs "hoàn trả sản phẩm").

**Ví dụ có độ tương tự THẤP:**
- **Câu A:** Shopee hoàn lại tiền qua Số Dư Tài Khoản Shopee trong 3-5 ngày làm việc.
- **Câu B:** Người bán cần chuẩn bị chứng từ đăng ký kinh doanh và mã số thuế.
- **Tại sao khác:** Câu A đề cập đến phương thức và thời gian hoàn tiền cho người mua, trong khi Câu B đề cập đến thủ tục hành chính và giấy tờ pháp lý của người bán.

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**
> Khoảng cách Euclid phụ thuộc trực tiếp vào độ dài (magnitude) của vector, khiến hai câu có cùng nội dung ngữ nghĩa nhưng độ dài từ khác nhau bị tính khoảng cách rất xa nhau. Độ tương tự Cosine chuẩn hóa độ dài vector về 1, chỉ đo góc hướng thể hiện ngữ nghĩa, giúp so sánh chính xác và công bằng giữa các văn bản có độ dài ngắn khác nhau.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> *Trình bày phép tính:*
> - Kích thước bước nhảy (stride / step size) = $\text{chunk\_size} - \text{overlap} = 500 - 50 = 450$ ký tự.
> - Chunk đầu tiên phủ phạm vi ký tự $[0, 500]$.
> - Phạm vi ký tự còn lại cần phủ = $10,000 - 500 = 9,500$ ký tự.
> - Số chunk bổ sung cần tạo = $\lceil \frac{9500}{450} \rceil = \lceil 21.11 \rceil = 22$ chunks.
> - Tổng số chunks = $1 + 21 = 22$ chunks (nếu tính theo điểm bắt đầu: $0, 450, 900, \dots, 9450$, tổng cộng 22 chunks).
> 
> *Đáp án:* **22 chunks**

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**
> - *Phép tính:* Stride mới = $500 - 100 = 400$ ký tự. Số chunk bổ sung = $\lceil \frac{9500}{400} \rceil = \lceil 23.75 \rceil = 24$ chunks. Tổng số chunk tăng lên thành **24 chunks**.
> - *Lý do muốn overlap nhiều hơn:* Tăng overlap giúp bảo toàn tối đa ngữ cảnh tại các ranh giới điểm cắt. Điều này ngăn chặn tình trạng một điều khoản quan trọng, một con số hạn mức hay điều kiện ngoại lệ bị cắt đôi ở ranh giới giữa 2 chunks dẫn đến mất mát thông tin khi tìm kiếm.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:
> Dùng biểu thức chính quy `re.split(r'(?<=[.!?])\s+', text)` để tách văn bản thành danh sách câu dựa trên các dấu kết thúc câu (`.`, `!`, `?`). Xử lý loại bỏ khoảng trắng rỗng và gom tối đa `max_sentences_per_chunk` câu vào một chunk. Điều này đảm bảo ngữ cảnh được giữ nguyên vẹn theo đơn vị câu hoàn chỉnh.

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:
> Áp dụng thuật toán đệ quy thử nghiệm danh sách phân cách ưu tiên giảm dần: `["\n\n", "\n", " ", ""]`. Thuật toán bắt đầu tách bằng ký tự phân cách lớn nhất; nếu khối thu được vẫn lớn hơn `chunk_size`, nó đệ quy tách tiếp bằng phân cách nhỏ hơn. Base case đạt được khi khối có độ dài $\le \text{chunk\_size}$ hoặc đã sử dụng ký tự phân cách rỗng. Sau đó ghép lại các khối nhỏ để đạt kích thước tối ưu.

**`HeadingSectionChunker.chunk_document` (Chiến lược nâng cao cá nhân)** — hướng tiếp cận:
> Phân tích cấu trúc ngữ nghĩa của Markdown thông qua các tiêu đề (`#`, `##`, `###`). Thuật toán xây dựng cây đường dẫn tiêu đề (`section_path`, ví dụ: `Chính sách... > 4. QUY ĐỊNH... > 4.2. Hạn mức`) và đính kèm trực tiếp vào siêu dữ liệu (`metadata`) của từng chunk. Giữ trọn vẹn nội dung của từng mục nếu tổng ký tự nằm trong `target_size` (800 ký tự), đồng thời bảo toàn nguyên vẹn cấu trúc bảng biểu (Markdown tables) và các khối lệnh/văn bản (`fences` ```text).

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:
> Lưu trữ văn bản dưới dạng danh sách `Document` và tính toán vector nhúng tương ứng bằng `embedder` được truyền vào (ví dụ `GeminiEmbedder`). Hàm `search` chuyển đổi query thành vector nhúng, duyệt qua danh sách lưu trữ để tính Cosine Similarity (`compute_similarity`), sắp xếp kết quả giảm dần theo điểm số score và trả về `top_k` chunk tốt nhất.

**`search_with_filter` + `delete_document`** — hướng tiếp cận:
> `search_with_filter` thực hiện tiền lọc (pre-filtering) danh sách các chunk sao cho siêu dữ liệu của chunk chứa đầy đủ các cặp khóa-giá trị trong `metadata_filter` (ví dụ `{"audience": "buyer"}`) trước khi tính toán độ tương tự vector. Hàm `delete_document` tìm kiếm tất cả các chunk có `doc_id` khớp với văn bản cần xóa, thực hiện loại bỏ khỏi danh sách và trả về `True` nếu xóa thành công.

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:
> Sử dụng `EmbeddingStore` để tìm kiếm `top_k` chunk liên quan nhất (có áp dụng filter nếu được cung cấp). Xây dựng hệ thống RAG Prompt ngặt nghèo, đưa toàn bộ nội dung các chunk truy xuất được vào phần ngữ cảnh (context), và chỉ thị mô hình chỉ được trả lời dựa trên ngữ cảnh này. Nếu không tìm thấy thông tin phù hợp, agent sẽ thông báo không đủ thông tin thay vì tự suy đoán.

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

```
============================= test session starts =============================
platform win32 -- Python 3.12.10, pytest-9.1.1, pluggy-1.6.0 -- E:\VinAI\K4-Day07-LuuQuangKhai-02599-Data-Foundations\.venv\Scripts\python.exe
cachedir: .pytest_cache
rootdir: E:\VinAI\K4-Day07-LuuQuangKhai-02599-Data-Foundations
plugins: anyio-4.15.1
collected 52 items

tests/test_edge_cases.py::TestEdgeCases::test_agent_prompt_uses_only_filtered_context PASSED [  1%]
tests/test_edge_cases.py::TestEdgeCases::test_cosine_checks_dimensions_and_ignores_magnitude PASSED [  3%]
tests/test_edge_cases.py::TestEdgeCases::test_prefilter_and_delete_all_parent_chunks PASSED [  5%]
tests/test_edge_cases.py::TestEdgeCases::test_recursive_preserves_text_and_bounds_with_missing_separators PASSED [  7%]
tests/test_edge_cases.py::TestEdgeCases::test_sentence_empty_and_punctuation PASSED [  9%]
tests/test_heading_chunking.py::TestHeadingSectionChunker::test_fences_empty_sections_and_plain_text PASSED [ 11%]
tests/test_heading_chunking.py::TestHeadingSectionChunker::test_metadata_is_not_mutated PASSED [ 13%]
tests/test_heading_chunking.py::TestHeadingSectionChunker::test_repeated_headings_and_soft_limit PASSED [ 15%]
tests/test_heading_chunking.py::TestHeadingSectionChunker::test_siblings_do_not_inherit_each_other PASSED [ 17%]
tests/test_heading_chunking.py::TestHeadingSectionChunker::test_table_headers_repeated_and_rows_preserved PASSED [ 19%]
tests/test_solution.py::TestProjectStructure::test_root_main_entrypoint_exists PASSED [ 21%]
tests/test_solution.py::TestProjectStructure::test_src_package_exists PASSED [ 23%]
tests/test_solution.py::TestClassBasedInterfaces::test_chunker_classes_exist PASSED [ 25%]
tests/test_solution.py::TestClassBasedInterfaces::test_mock_embedder_exists PASSED [ 26%]
tests/test_solution.py::TestFixedSizeChunker::test_chunks_respect_size PASSED [ 28%]
tests/test_solution.py::TestFixedSizeChunker::test_correct_number_of_chunks_no_overlap PASSED [ 30%]
tests/test_solution.py::TestFixedSizeChunker::test_empty_text_returns_empty_list PASSED [ 32%]
tests/test_solution.py::TestFixedSizeChunker::test_no_overlap_no_shared_content PASSED [ 34%]
tests/test_solution.py::TestFixedSizeChunker::test_overlap_creates_shared_content PASSED [ 36%]
tests/test_solution.py::TestFixedSizeChunker::test_returns_list PASSED    [ 38%]
tests/test_solution.py::TestFixedSizeChunker::test_single_chunk_if_text_shorter PASSED [ 40%]
tests/test_solution.py::TestSentenceChunker::test_chunks_are_strings PASSED [ 42%]
tests/test_solution.py::TestSentenceChunker::test_respects_max_sentences PASSED [ 44%]
tests/test_solution.py::TestSentenceChunker::test_returns_list PASSED    [ 46%]
tests/test_solution.py::TestSentenceChunker::test_single_sentence_max_gives_many_chunks PASSED [ 48%]
tests/test_solution.py::TestRecursiveChunker::test_chunks_within_size_when_possible PASSED [ 50%]
tests/test_solution.py::TestRecursiveChunker::test_empty_separators_falls_back_gracefully PASSED [ 51%]
tests/test_solution.py::TestRecursiveChunker::test_handles_double_newline_separator PASSED [ 53%]
tests/test_solution.py::TestRecursiveChunker::test_returns_list PASSED   [ 55%]
tests/test_solution.py::TestEmbeddingStore::test_add_documents_increases_size PASSED [ 57%]
tests/test_solution.py::TestEmbeddingStore::test_add_more_increases_further PASSED [ 59%]
tests/test_solution.py::TestEmbeddingStore::test_initial_size_is_zero PASSED [ 61%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_content_key PASSED [ 63%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_score_key PASSED [ 65%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_sorted_by_score_descending PASSED [ 67%]
tests/test_solution.py::TestEmbeddingStore::test_search_returns_at_most_top_k PASSED [ 69%]
tests/test_solution.py::TestEmbeddingStore::test_search_returns_list PASSED [ 71%]
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_non_empty PASSED [ 73%]
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_returns_string PASSED [ 75%]
tests/test_solution.py::TestComputeSimilarity::test_identical_vectors_return_1 PASSED [ 76%]
tests/test_solution.py::TestComputeSimilarity::test_opposite_vectors_return_minus_1 PASSED [ 78%]
tests/test_solution.py::TestComputeSimilarity::test_orthogonal_vectors_return_0 PASSED [ 80%]
tests/test_solution.py::TestComputeSimilarity::test_zero_vector_returns_0 PASSED [ 82%]
tests/test_solution.py::TestCompareChunkingStrategies::test_counts_are_positive PASSED [ 84%]
tests/test_solution.py::TestCompareChunkingStrategies::test_each_strategy_has_count_and_avg_length PASSED [ 86%]
tests/test_solution.py::TestCompareChunkingStrategies::test_returns_three_strategies PASSED [ 88%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_filter_by_department PASSED [ 90%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_no_filter_returns_all_candidates PASSED [ 92%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_returns_at_most_top_k PASSED [ 94%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_reduces_collection_size PASSED [ 96%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_false_for_nonexistent_doc PASSED [ 98%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_true_for_existing_doc PASSED [100%]

============================= 52 passed in 0.08s ==============================
```

**Số lượng bài test vượt qua (pass):** **52 / 52** (Bao gồm 42 tests cơ sở + 10 edge cases & test HeadingSectionChunker).

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

Thực nghiệm đo độ tương tự Cosine thực tế sử dụng mô hình **Gemini Embedding (`gemini-embedding-001`)**:

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | Shopee hoàn lại tiền qua Số Dư Tài Khoản Shopee trong 3-5 ngày làm việc. | Khách hàng nhận được tiền hoàn trả vào tài khoản Shopee sau 3 đến 5 ngày. | cao | 0.8952 | Đúng |
| 2 | Người mua hạng Vàng và Kim Cương được áp dụng quyền Trả hàng COM. | Thành viên ShopeeVIP có hạn mức trả hàng tối đa 15 lần một tháng. | cao | 0.7681 | Đúng |
| 3 | Người bán phải phản hồi trong vòng 02 ngày lịch kể từ khi nhận thông báo. | Thời gian phản hồi của Người Bán cho yêu cầu hoàn tiền là 48 giờ. | cao | 0.8624 | Đúng |
| 4 | Chi phí vận chuyển chiều hoàn trả do Shopee hoặc Người bán chi trả. | Hướng dẫn cài đặt ứng dụng Shopee trên hệ điều hành Android và iOS. | thấp | 0.3120 | Đúng |
| 5 | Sản phẩm mua tại Shopee Mall được miễn phí vận chuyển chiều trả hàng. | Đối với sản phẩm không thuộc Shopee Mall, người mua tự trả phí và được hỗ trợ Shopee Xu. | cao | 0.7943 | Đúng |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**
> Kết quả ở **Cặp 5** (Shopee Mall vs Sản phẩm không thuộc Shopee Mall) và **Cặp 2** là bất ngờ nhất. Mặc dù câu A và câu B đề cập đến 2 quy định trái ngược hoặc 2 đối tượng chính sách hoàn toàn khác nhau, Gemini Embedder vẫn trả về điểm tương đồng khá cao (~0.77 - 0.79). Điều này chứng minh embedding biểu diễn ý nghĩa dựa trên không gian khái niệm chủ đề tổng thể (cùng thuộc không gian "chính sách đổi trả Shopee"), chứ không tự phân biệt được các logic điều kiện trái ngược nếu không có bước lọc metadata (`metadata_filter`) hỗ trợ.

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Chạy **5 câu hỏi đánh giá của nhóm** trên chiến lược cá nhân `HeadingSectionChunker` kết hợp mô hình nhúng **Gemini Embedding (`gemini-embedding-001`)** (bộ dữ liệu 10 tài liệu Shopee, 164 chunks).

| # | Câu hỏi (Query) | Top-1 Chunk truy xuất được (tóm tắt) | Điểm Score | Có liên quan không? (Relevant) | Câu trả lời của Agent (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | Người mua nào đủ điều kiện Trả hàng COM, hạn mức của ShopeeVIP là bao nhiêu và trường hợp nào bị loại trừ? | `shopee-chinh-sach-tra-hang-nguoi-mua:heading:17` (`Chính sách... > 4. QUY ĐỊNH BỔ SUNG... > 4.2. Hạn mức`) | 0.8724 | Có (Top 1, 2, 3 chứa đầy đủ Hạng Vàng/Kim Cương & ShopeeVIP) | Người mua hạng Vàng, Kim Cương hoặc dùng ShopeeVIP đủ điều kiện Trả hàng COM. ShopeeVIP được áp hạn mức cao hơn, không cộng dồn tháng trước và bị chấm dứt khi gói hết hiệu lực. |
| 2 | Người bán phải phản hồi yêu cầu Trả hàng/Hoàn tiền trong bao lâu, và điều gì xảy ra nếu không phản hồi đúng hạn? | `shopee-chinh-sach-tra-hang-nguoi-ban:heading:23` (`Chính sách... > 5. QUYỀN CỦA NGƯỜI BÁN`) | 0.7874 | Có (Trích chính xác thời hạn 02 ngày lịch & hậu quả) | Người bán cần phản hồi trong vòng 02 ngày lịch. Nếu không phản hồi đúng hạn, Shopee hiểu người bán đồng ý với quyết định xử lý và có thể tự động hoàn tiền cho người mua. |
| 3 | Theo chính sách dành cho người bán, trường hợp nào người bán chịu chi phí vận chuyển chiều hoàn trả và trường hợp nào không phải chịu? | `shopee-chinh-sach-tra-hang-nguoi-ban:heading:25` (`Chính sách... > 7. TRÁCH NHIỆM VỀ CHI PHÍ... > 7.1. Người Bán chịu...`) | 0.8326 | Có (Top 1 chứa các TH chịu phí, Top 2 & 3 chứa các TH không chịu phí) | Người bán chịu phí khi đơn được Shopee chấp thuận không do lỗi người mua/DVVC, đơn giao không thành công. Người bán không chịu phí khi hoàn tiền ngay không trả hàng, đơn kênh tự vận chuyển giao không thành công, tự sắp xếp trả hàng, khiếu nại một phần hoặc lý do Chưa nhận được hàng. |
| 4 | Nếu người mua tự sắp xếp trả hàng, chính sách hoàn chi phí khác nhau thế nào giữa sản phẩm Shopee Mall và sản phẩm không thuộc Shopee Mall? | `shopee-chinh-sach-tra-hang-nguoi-mua:heading:23` (`Chính sách... > 8. TRÁCH NHIỆM VỀ CHI PHÍ... > 8.1. Với Sản Phẩm mua tại Shopee Mall...`) | 0.8630 | Có (Top 1 cho Shopee Mall, Top 3 cho sản phẩm ngoài Mall) | Với Shopee Mall, Shopee hoàn lại đúng số tiền phí vận chuyển đã trả vào Số Dư Tài Khoản Shopee trong 3-5 ngày làm việc. Với sản phẩm không thuộc Shopee Mall, Shopee hỗ trợ một phần phí dưới dạng Shopee Xu trong 3-5 ngày làm việc nếu đủ điều kiện. |
| 5 | Nếu người bán đề xuất Hoàn tiền ngay, mức hoàn tối thiểu là bao nhiêu và người mua có lựa chọn gì nếu không đồng ý? | `shopee-chinh-sach-tra-hang-nguoi-ban:heading:31` (`Chính sách... > 9. HOÀN TIỀN... > 9.5.`) | 0.7523 | Có (Top 1 & 2 chứa quy định $\ge 50\%$, Top 3 chứa quy trình xử lý tiếp) | Mức hoàn tiền ngay do người bán đề xuất không được thấp hơn 50% giá trị sản phẩm hoàn trả. Nếu người mua không đồng ý, người mua có thể lựa chọn phương án Trả hàng & Hoàn tiền theo quy trình xử lý của Shopee. |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** **5 / 5** (Đạt độ chính xác 100%).

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**
> Việc kết hợp phân chia theo tiêu đề ngữ nghĩa (`HeadingSectionChunker`) với siêu dữ liệu đường dẫn mục (`section_path` breadcrumbs) giúp mô hình nhúng Gemini định vị tuyệt đối chính xác các điều khoản chi tiết trong văn bản pháp lý dài. Kết hợp với việc tiền lọc theo `audience` (`buyer` / `seller`), hệ thống loại bỏ hoàn toàn nhiễu thông tin giữa hai góc độ đối tượng, giúp RAG Agent sinh câu trả lời căn cứ (grounded) đạt điểm tối đa.

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
