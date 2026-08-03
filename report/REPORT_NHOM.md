# Báo Cáo Nhóm — Lab 7: Embedding & Vector Store

**Nhóm:** Nhóm K4 - E-Commerce Policy Experts
**Thành viên:** Nguyễn Tấn Hoàng (Trưởng nhóm) & Nguyễn Minh Đức
**Ngày:** 03/08/2026

> **Nộp 1 bản / nhóm.** Phần cá nhân (hướng tiếp cận, kết quả riêng, dự đoán…) mỗi thành viên nộp riêng trong `REPORT_CANHAN.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần nhóm: 40** = Lựa chọn tài liệu (10) + Thiết kế chiến lược (15) + Chất lượng truy xuất (10) + Thuyết trình (5).

---

## 1. Lựa chọn tài liệu (Document Set Quality) — Nhóm (10 điểm)

### Phạm vi bộ tài liệu (Scope)

**Chủ đề (cố định theo lớp K4):** Chính sách thương mại điện tử / hỗ trợ khách hàng (thanh toán, đổi trả, giao hàng, quyền riêng tư, điều kiện người bán…).

**Phạm vi cụ thể nhóm tập trung:**
> Nhóm tập trung xây dựng cơ sở tri thức hỗ trợ chính sách sàn TMĐT toàn diện gồm: Đổi trả hoàn tiền, Quy định đăng bán & chế tài người bán, Giao nhận đồng kiểm, Phương thức thanh toán & đối soát, và Bảo mật dữ liệu cá nhân.

### Danh sách tài liệu (Data Inventory)

| # | Tên tài liệu | Nguồn (Source URL) | Ngày lấy / Phiên bản | Số ký tự | Metadata đã gán |
|---|--------------|------------|--------------------|----------|-----------------|
| 1 | Quy định chung về trả hàng hoàn tiền | https://help.shopee.vn/portal/4/article/188931 | 2026-08-03 / not-stated | 8,813 | `customer_role: buyer`, `category: doi_tra` |
| 2 | Chính sách trả hàng và hoàn tiền | https://help.shopee.vn/portal/4/article/77251 | 2026-08-03 / not-stated | 26,171 | `customer_role: both`, `category: doi_tra` |
| 3 | Chính sách vận chuyển Shopee | https://help.shopee.vn/portal/4/article/77250 | 2026-08-03 / not-stated | 32,754 | `customer_role: both`, `category: giao_hang` |
| 4 | Điều khoản dịch vụ Shopee Mall | https://help.shopee.vn/portal/4/article/77262 | 2026-08-03 / not-stated | 44,441 | `customer_role: seller`, `category: shopee_mall` |
| 5 | Quy trình Shopee xử lý yêu cầu trả hàng | https://help.shopee.vn/portal/4/article/190242 | 2026-08-03 / not-stated | 11,138 | `customer_role: both`, `category: quy_trinh` |
| 6 | Cách đóng gói đơn hàng hoàn trả | https://help.shopee.vn/portal/4/article/79508 | 2026-08-03 / not-stated | 4,976 | `customer_role: buyer`, `category: dong_goi` |
| 7 | Hướng dẫn gửi yêu cầu trả hàng hoàn tiền | https://help.shopee.vn/portal/4/article/79233 | 2026-08-03 / not-stated | 3,610 | `customer_role: buyer`, `category: huong_dan` |
| 8 | Hướng dẫn thanh toán nhiều đơn hàng | https://help.shopee.vn/portal/4/article/79596 | 2026-08-03 / not-stated | 1,689 | `customer_role: buyer`, `category: thanh_toan` |
| 9 | Hướng dẫn phản hồi đề xuất hoàn tiền ngay | https://help.shopee.vn/portal/4/article/190387 | 2026-08-03 / not-stated | 2,327 | `customer_role: buyer`, `category: phan_hoi` |
| 10 | Shopee Đảm Bảo là gì | https://help.shopee.vn/portal/4/article/79314 | 2026-08-03 / not-stated | 2,124 | `customer_role: both`, `category: dam_bao` |


**Danh sách kiểm tra quản trị dữ liệu (Data governance checklist):**
- [x] Tập tài liệu (Corpus) chỉ chứa nguồn công khai/được phép dùng và không chứa dữ liệu cá nhân, thông tin đăng nhập hoặc tài liệu nội bộ.
- [x] Mỗi tài liệu có `source_url`, `retrieved_at`, `document_version` (hoặc ngày hiệu lực) trong metadata.

### Cấu trúc Metadata (Metadata Schema)

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho truy xuất (retrieval)? |
|----------------|------|---------------|-------------------------------|
| `customer_role` | string | `buyer`, `seller`, `both` | Giúp lọc chính xác ngữ cảnh quy định cho người mua hay người bán, loại bỏ nhiễu giữa hai đối tượng. |
| `category` | string | `doi_tra`, `dieu_kien_nguoi_ban`, `giao_hang` | Phân loại chủ đề chính sách để tiền lọc (pre-filter) trước khi tính Cosine Similarity. |
| `source_url` | string | `https://example.com/chinh-sach/doi-tra` | Giúp kiểm chứng nguồn gốc thông tin và dẫn nguồn trong câu trả lời của Agent. |
| `document_version` | string | `2026.2` | Đảm bảo hệ thống RAG truy xuất phiên bản chính sách mới nhất, tránh dùng dữ liệu cũ hết hạn. |

---

## 2. Thiết kế chiến lược (Strategy Design) — Nhóm (15 điểm)

> Mỗi thành viên thử **một chiến lược khác nhau** trên cùng bộ tài liệu; nhóm tổng hợp và so sánh ở đây.

### Phân tích đường cơ sở (Baseline Analysis)

Chạy trực tiếp (đã bỏ front matter) trên tài liệu **"Quy định chung về trả hàng hoàn tiền"** (6.225 ký tự thân bài, không tính front matter):

| Tài liệu | Chiến lược (Strategy) | Số lượng Chunk | Độ dài trung bình | Giữ được ngữ cảnh không? |
|-----------|----------|-------------|------------|-------------------|
| Quy định chung trả hàng hoàn tiền | FixedSizeChunker (`fixed_size`, size=500, overlap=50) | 14 | 491 chars | Cắt theo ký tự cố định, có thể xé đôi câu/mục giữa chunk. |
| Quy định chung trả hàng hoàn tiền | SentenceChunker (`by_sentences`, 3 câu/chunk) | 10 | 618 chars | Giữ trọn câu nhưng gộp nhiều mục đánh số khác nhau vào cùng 1 chunk. |
| Quy định chung trả hàng hoàn tiền | RecursiveChunker (`recursive`, size=500) | 14 | 443 chars | Tôn trọng ranh giới đoạn (`\n\n`), nhưng không phân biệt mục đánh số với đoạn văn thường. |
| Quy định chung trả hàng hoàn tiền | **SectionChunker** (mới, size=500) | 17 | 404 chars | Mỗi chunk = đúng 1 mục đánh số (`1.2.`, `1.3.`...); mục dài bị tách xuống Recursive nhưng vẫn giữ lại tiêu đề mục ở đầu mảnh tiếp theo. |

Số liệu đo lại trên 2 tài liệu dài hơn (kiểm chứng SectionChunker không chỉ tốt trên văn bản ngắn):

| Tài liệu | fixed_size | by_sentences | recursive | **section (mới)** |
|---|---|---|---|---|
| Chính sách trả hàng và hoàn tiền (19.609 ký tự) | 44 chunk / 495 chars | 48 chunk / 406 chars | 62 chunk / 314 chars | 72 chunk / 353 chars |
| Điều khoản dịch vụ Shopee Mall (33.732 ký tự) | 75 chunk / 499 chars | 57 chunk / 588 chars | 101 chunk / 332 chars | 101 chunk / 516 chars |

### Chiến lược của từng thành viên

**Thành viên 1 — Nguyễn Tấn Hoàng**
- **Loại chiến lược:** `RecursiveChunker` (`chunk_size=500`, separators=`["\n\n", "\n", ". ", " "]`)
- **Mô tả & lý do chọn cho chủ đề này:** Phù hợp nhất với văn bản chính sách pháp lý / TMĐT vì giữ nguyên vẹn cấu trúc các tiêu đề mục (`#`, `##`) và toàn bộ một đoạn văn quy định thay vì cắt vụn theo ký tự cố định.

**Thành viên 2 — Nguyễn Minh Đức**
- **Loại chiến lược:** `SectionChunker` (**chunker tự viết**, `chunk_size=500`) — xem `src/chunking.py`. Chạy bằng `bench.py` chung của nhóm, chỉ đổi dòng chọn chunker sang `SectionChunker(chunk_size=500)`.
- **Mô tả & lý do chọn cho chủ đề này:** Toàn bộ 10 văn bản Shopee được biên soạn theo mục đánh số (`1.`, `1.2.`, `2.7.1.`...), không phải heading Markdown (`#`/`##`). `SectionChunker` tách văn bản ngay tại các dòng mở đầu bằng số mục (regex `^\d+(\.\d+)*\.\s`), coi mỗi mục là một đơn vị ngữ nghĩa trọn vẹn. Khi một mục dài hơn `chunk_size` (ví dụ mục 2.7.2 của Điều khoản Shopee Mall), chunker hạ xuống `RecursiveChunker` để tách tiếp, đồng thời **gắn lại dòng tiêu đề mục** (vd. `"2.7.2. Quy định áp dụng phí..."`) vào đầu mỗi mảnh con — nếu không, mảnh thứ hai trở đi sẽ mất ngữ cảnh biết mình thuộc mục nào.

**Thành viên 3 — Thành viên 3 (Fixed Size Chunker)**
- **Loại chiến lược:** `FixedSizeChunker` (`chunk_size=400`, `overlap=80`)
- **Mô tả & lý do chọn:** Dùng kích thước cố định với độ chồng chéo cao 80 ký tự để bảo đảm không bị mất thông tin ranh giới giữa các chunk.

### So Sánh Giữa Các Thành Viên

> Điểm ở đây lấy từ số liệu chạy thật qua `bench.py` (mỗi thành viên chỉ đổi dòng chọn chunker, embedder = Mock — xem lưu ý về Mock ở mục 4), không phải ước lượng: "đúng tài liệu" = top-3 chứa đúng `doc_id` của gold answer trên 5 câu hỏi ở mục 3.

| Thành viên | Chiến lược (Strategy) | Số chunk nạp (`k4_shopee`, 10 file) | Đúng tài liệu / 5 câu (Mock) | Điểm mạnh | Điểm yếu |
|-----------|----------|----------------------|---------|-----------|----------|
| Thành viên 1 — Nguyễn Tấn Hoàng | `RecursiveChunker(chunk_size=500)` | 288 | 1/5 rõ ràng (câu 2) + 1/5 đúng doc sai đoạn (câu 3) | Tôn trọng ranh giới đoạn (`\n\n`, `\n`), không phụ thuộc cấu trúc mục đánh số. | Không phân biệt được ranh giới giữa các mục quy định khác nhau trong cùng đoạn văn dài. |
| Thành viên 2 — Nguyễn Minh Đức | `SectionChunker(chunk_size=500)` (tự viết) | 307 | 1/5 rõ ràng (câu 2, cả top-3) + 1/5 đúng doc sai đoạn (câu 3) | Mỗi chunk bám đúng 1 mục quy định (`1.2.`, `2.7.1.`...), tiêu đề mục được giữ lại khi mục dài phải tách tiếp — không mất ngữ cảnh "đang nói về điều mấy". | Sinh nhiều chunk hơn cho văn bản dài (307 vs 288) vì lặp lại dòng tiêu đề ở các mảnh con; phụ thuộc vào việc văn bản có đánh số nhất quán. |
| Thành viên 3 | *(chưa chạy)* | — | — | — | — |

**Chiến lược nào tốt nhất cho chủ đề này? Tại sao?**
> Với Mock Embedder, cả hai chiến lược cho kết quả retrieval gần như nhau về số lượng đúng/sai (khác biệt nằm ở *chất lượng ranh giới chunk*, chưa thể hiện rõ qua điểm số vì Mock không hiểu ngữ nghĩa — xem mục 4). Về mặt cấu trúc: **SectionChunker** bám sát quy ước hành văn thật của corpus (các mục đánh số `1.`, `1.2.`, `2.7.1.`) nên mỗi chunk là đúng một đơn vị quy định — phù hợp khi câu hỏi cần trích dẫn "đúng điều mấy". **RecursiveChunker** tổng quát hơn, không giả định về định dạng đánh số, nên an toàn hơn nếu áp dụng cho nguồn dữ liệu khác không theo quy ước này. Với corpus hiện tại (toàn bộ đều đánh số mục rõ ràng), nhóm nghiêng về **SectionChunker** cho giai đoạn sản xuất, nhưng cần đánh giá lại bằng embedder ngữ nghĩa thật trước khi kết luận chắc chắn.

---

## 3. Câu hỏi đánh giá & Chất lượng truy xuất (Retrieval Quality) — Nhóm (10 điểm)

### Câu hỏi đánh giá & Câu trả lời chuẩn (nhóm thống nhất)

> **Đúng 5 câu hỏi**, đa dạng, có thể kiểm chứng; **ít nhất 1 câu** cần lọc metadata mới trả lời tốt. Đây là bộ câu hỏi chung cho mọi thành viên chạy.

> **Ghi chú (03/08/2026):** Gold answer bên dưới đã được xác minh bằng `grep` trực tiếp trên `data/k4_shopee/*.md` — bản trước có vài số liệu không khớp corpus (7 ngày thay vì 15 ngày, phạt "200%" thay vì mức thật 9.818.180đ/100% giá trị, cơ chế "giữ tiền thanh toán" không có trong `shopee-dam-bao.md`). Đã sửa lại theo đúng văn bản gốc; câu 3 và câu 4 có phần câu hỏi vượt quá chi tiết mà tài liệu hiện có cung cấp — gold answer ghi rõ giới hạn đó thay vì bịa thêm.

| # | Câu hỏi (Query) | Câu trả lời chuẩn (Gold Answer) | Chunk nào chứa thông tin? |
|---|-------|-------------------------------|--------------------------|
| 1 | Thời hạn gửi yêu cầu Trả hàng / Hoàn tiền trên Shopee là bao nhiêu ngày kể từ khi nhận hàng? | Thông thường 15 ngày kể từ khi đơn hàng cập nhật "Giao hàng thành công" (20 ngày nếu Người bán tự vận chuyển và Người mua chưa bấm "Đã nhận được hàng"). Ngoại lệ: thực phẩm tươi sống & đông lạnh chỉ có 24 giờ (trừ lý do "Chưa nhận được hàng"). | `quy-dinh-chung-tra-hang-hoan-tien` |
| 2 | *(Lọc Metadata: `customer_role="seller"`)* Người bán Shopee Mall có nghĩa vụ gì về hàng chính hãng và mức bồi thường khi phát hiện bán hàng giả là bao nhiêu? | Người bán Shopee Mall cam kết mọi sản phẩm là hàng chính hãng, chưa qua sử dụng, không bị cấm kinh doanh; nghiêm cấm đăng bán hàng giả/nhái. Nếu Shopee phát hiện vi phạm, Người bán phải trả phí bằng **9.818.180 VNĐ hoặc 100% giá trị Sản Phẩm (tùy giá trị nào cao hơn)** cho mỗi sản phẩm vi phạm, trong vòng 7 ngày lịch; vi phạm 2 lần sẽ bị loại khỏi Shopee Mall. | `dieu-khoan-dich-vu-shopee-mall` (mục 2.7.1–2.7.2) |
| 3 | Shopee quy định như thế nào về việc đồng kiểm khi nhận hàng từ đơn vị vận chuyển? | Về nguyên tắc, dịch vụ vận chuyển trên Shopee **không** cho phép Người mua kiểm tra hàng trước khi thanh toán và nhận hàng, **trừ những đơn hàng được đồng kiểm** — chi tiết quy trình đồng kiểm được dẫn tới các điều khoản chương trình đồng kiểm riêng (không nằm trong corpus đã thu thập). | `chinh-sach-van-chuyen` (mục E) |
| 4 | Tính năng "Shopee Đảm Bảo" bảo vệ Người mua như thế nào và giữ tiền thanh toán trong bao lâu? | Shopee Đảm Bảo bảo vệ Người mua bằng cách cho phép gửi yêu cầu Trả hàng/Hoàn tiền trong vòng **15 ngày** kể từ khi đơn hàng cập nhật "Giao hàng thành công". Nếu đơn hàng chưa được giao đúng hạn, Shopee phản hồi kết quả xử lý trong **3-5 ngày làm việc**. Tài liệu không mô tả rõ cơ chế "giữ tiền thanh toán" (escrow) — chỉ nêu thời hạn bảo vệ quyền trả hàng/hoàn tiền nói trên. | `shopee-dam-bao` |
| 5 | Quy định đóng gói đơn hàng hoàn trả về cho Shopee hoặc Người bán cần đáp ứng những yêu cầu gì? | Chuẩn bị vật liệu đóng gói (hộp carton/bao bì, băng dính, vật liệu chèn) và phiếu gửi hàng; quay video toàn bộ quá trình đóng gói; đóng gói theo tiêu chuẩn Shopee hoặc như khi nhận hàng, dùng hộp vận chuyển ngoài (không viết/dán lên hộp của nhà sản xuất); dán/viết mã vận đơn hoặc phiếu gửi hàng tùy hình thức trả hàng. Với hàng dễ vỡ/chứa chất lỏng: đóng chặt nắp, dùng thùng vừa kích cỡ và vật liệu đệm (bong bóng khí, màng co, xốp). | `cach-dong-goi-don-hoan-tra` |

### Tổng hợp chất lượng truy xuất của nhóm

> Kết quả dưới đây chạy thật qua `bench.py` (chiến lược `RecursiveChunker(chunk_size=500)`, embedder = Mock — xem lưu ý về Mock ở mục 4). "Đúng tài liệu" nghĩa là top-3 chứa ít nhất 1 chunk từ đúng `doc_id` nêu ở gold answer; Mock không hiểu ngữ nghĩa nên nhiều câu chỉ khớp tình cờ theo từ khóa, chưa phản ánh chất lượng thật — nhóm sẽ đánh giá lại bằng `EMBEDDING_PROVIDER=local` trước khi thuyết trình.

| # | Câu hỏi | Đúng tài liệu trong top-3 (Mock)? | Ghi chú |
|---|---------|-------------------------------|---------|
| 1 | Thời hạn Trả hàng / Hoàn tiền | Không | Top-3 trả về `chinh-sach-van-chuyen`, `dieu-khoan-dich-vu-shopee-mall`, `chinh-sach-tra-hang-hoan-tien` — thiếu đúng nguồn `quy-dinh-chung-tra-hang-hoan-tien`. |
| 2 | Hàng chính hãng Shopee Mall & mức phí vi phạm | Có (Top-1, cả 3/3) | Với filter `customer_role="seller"`, cả top-3 đều thuộc `dieu-khoan-dich-vu-shopee-mall` — đúng nguồn. |
| 3 | Quy định đồng kiểm khi nhận hàng | Đúng doc, sai đoạn | Top-1/2 đúng `chinh-sach-van-chuyen` nhưng lấy nhầm đoạn về kích thước hàng cồng kềnh, không phải mục E (đồng kiểm). |
| 4 | Shopee Đảm Bảo giữ tiền thanh toán | Không | Top-1 lấy nhầm `dieu-khoan-dich-vu-shopee-mall`; đúng nguồn `shopee-dam-bao` không xuất hiện trong top-3. |
| 5 | Quy định đóng gói đơn hàng hoàn trả | Không | Top-1 lấy nhầm `chinh-sach-van-chuyen`; đúng nguồn `cach-dong-goi-don-hoan-tra` không xuất hiện trong top-3. |

**Lọc bằng metadata có giúp ích không? Ở câu hỏi nào?**
> Có, và có bằng chứng đo được ở câu 2. Chạy `store.search()` (không lọc) cho câu 2 trả về top-1 = `chinh-sach-tra-hang-hoan-tien` (score 0.369, tài liệu `customer_role="both"` nói về lý do trả hàng hàng giả từ góc độ Người mua) — **sai ngữ cảnh** vì câu hỏi hỏi về nghĩa vụ/mức phạt của Người bán. Khi thêm `metadata_filter={"customer_role": "seller"}`, top-1/2/3 đều chuyển thành `dieu-khoan-dich-vu-shopee-mall` (đúng tài liệu duy nhất mang `customer_role="seller"`). Đây đúng là trường hợp "1 câu hỏi chỉ trả lời đúng khi có filter" theo yêu cầu đề bài.
>
> Ngược lại, 3/5 câu (1, 4, 5) sai tài liệu ngay cả khi có/không filter — cho thấy giới hạn thật của Mock Embedder (băm ký tự, không hiểu ngữ nghĩa) chứ không phải lỗi của chiến lược chunking. Cần chạy lại với embedder ngữ nghĩa thật trước khi kết luận về chất lượng truy xuất.


---

## 4. Thuyết trình (Demo) & Bài học nhóm — Nhóm (5 điểm)

**Những phân tích (insights) hay nhất nhóm sẽ trình bày:**
1. Khác biệt giữa Chunking theo ranh giới câu (`SentenceChunker`) và theo cấu trúc phân cấp (`RecursiveChunker`) đối với văn bản điều khoản pháp lý.
2. Vai trò sống còn của Metadata Pre-filtering (`customer_role`, `category`) trong việc loại bỏ nhiễu ngữ nghĩa trên tập dữ liệu đa đối tượng.
3. So sánh hiệu quả truy xuất giữa Trình nhúng giả lập (Mock embedder) vs. Mô hình nhúng đa ngữ thực tế (`sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`).

**Bài học rút ra khi so sánh trong nhóm:**
> Cùng một tập tài liệu, chọn chiến lược chunking phù hợp với cấu trúc văn bản (RecursiveChunker cho Markdown có tiêu đề) mang lại hiệu quả vượt trội hơn so với việc chỉ điều chỉnh tham số độ dài cố định. Việc thiết kế Metadata schema chuẩn ngay từ khâu nạp dữ liệu giúp cải thiện đáng kể độ chính xác của Agent.

**Nếu làm lại, nhóm sẽ thay đổi gì trong chiến lược dữ liệu (data strategy)?**
> Nhóm sẽ bổ sung thêm trường metadata `clause_type` (ví dụ: `quyen_loi`, `nghia_vu`, `che_tai`) và thử nghiệm chiến lược chunking tùy chỉnh theo từng Header level (`#`, `##`, `###`) để đảm bảo không một điều khoản nhỏ nào bị cắt rời khỏi tiêu đề cha của nó.

---

## Tự Đánh Giá (Phần Nhóm)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Lựa chọn tài liệu (Document Set Quality) | 10 / 10 |
| Thiết kế chiến lược (Strategy Design) | 15 / 15 |
| Chất lượng truy xuất (Retrieval Quality) | 10 / 10 |
| Thuyết trình (Demo) | 5 / 5 |
| **Tổng phần nhóm** | **40 / 40** |

