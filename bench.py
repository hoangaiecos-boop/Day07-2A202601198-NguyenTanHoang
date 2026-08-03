"""
bench.py — benchmark chiến lược chunking cá nhân (Nguyễn Tấn Hoàng).

Chiến lược riêng: RecursiveChunker(chunk_size=500) — DÒNG DUY NHẤT khác với
các thành viên khác trong nhóm. Mọi phần còn lại (corpus, embedder, 5 câu hỏi)
dùng chung để so sánh công bằng.
"""
from __future__ import annotations

from pathlib import Path

from dotenv import load_dotenv

from ingest import build_knowledge_base
from src.agent import KnowledgeBaseAgent
from src.chunking import RecursiveChunker
from src.embeddings import (
    EMBEDDING_PROVIDER_ENV,
    LOCAL_EMBEDDING_MODEL,
    LocalEmbedder,
    OpenAIEmbedder,
    OPENAI_EMBEDDING_MODEL,
    _mock_embed,
)

import os

DATA_DIR = "data/k4_shopee"

# 5 câu hỏi chốt chung của nhóm (xem report/REPORT_NHOM.md, mục 3).
QUERIES: list[tuple[str, dict | None]] = [
    ("Thời hạn gửi yêu cầu Trả hàng / Hoàn tiền trên Shopee là bao nhiêu ngày kể từ khi nhận hàng?", None),
    ("Người bán Shopee Mall có nghĩa vụ gì về hàng chính hãng và mức bồi thường khi phát hiện bán hàng giả là bao nhiêu?", {"customer_role": "seller"}),
    ("Shopee quy định như thế nào về việc đồng kiểm khi nhận hàng từ đơn vị vận chuyển?", None),
    ("Tính năng 'Shopee Đảm Bảo' bảo vệ Người mua như thế nào và giữ tiền thanh toán trong bao lâu?", None),
    ("Quy định đóng gói đơn hàng hoàn trả về cho Shopee hoặc Người bán cần đáp ứng những yêu cầu gì?", None),
]


def _select_embedder():
    load_dotenv(override=False)
    provider = os.getenv(EMBEDDING_PROVIDER_ENV, "mock").strip().lower()
    if provider == "local":
        try:
            return LocalEmbedder(model_name=os.getenv("LOCAL_EMBEDDING_MODEL", LOCAL_EMBEDDING_MODEL))
        except Exception:
            print("Local embedder không sẵn sàng; tạm dùng mock.")
            return _mock_embed
    if provider == "openai":
        try:
            return OpenAIEmbedder(model_name=os.getenv("OPENAI_EMBEDDING_MODEL", OPENAI_EMBEDDING_MODEL))
        except Exception:
            print("OpenAI embedder không sẵn sàng; tạm dùng mock.")
            return _mock_embed
    return _mock_embed


def demo_llm(prompt: str) -> str:
    preview = prompt[:400].replace("\n", " ")
    return f"[DEMO LLM] {preview}..."


def main() -> int:
    if not Path(DATA_DIR).exists():
        print(f"Không tìm thấy thư mục dữ liệu: {DATA_DIR}")
        return 1

    # 1. Chọn chunker của riêng bạn.
    chunker = RecursiveChunker(chunk_size=500)

    embedder = _select_embedder()
    backend = getattr(embedder, "_backend_name", embedder.__class__.__name__)

    # 2. Nạp cả thư mục corpus.
    store = build_knowledge_base(DATA_DIR, embedder, chunker=chunker)

    print(f"Chiến lược: {chunker.__class__.__name__}(chunk_size={chunker.chunk_size})")
    print(f"Backend nhúng: {backend}")
    print(f"Số chunk đã nạp: {store.get_collection_size()}")

    agent = KnowledgeBaseAgent(store=store, llm_fn=demo_llm)

    # 3. Chạy 5 query, in top-3 (score, doc_id, preview) + câu trả lời agent.
    for i, (question, metadata_filter) in enumerate(QUERIES, start=1):
        print(f"\n=== Câu {i}: {question}")
        if metadata_filter:
            print(f"    (lọc metadata: {metadata_filter})")
            results = store.search_with_filter(question, metadata_filter=metadata_filter, top_k=3)
        else:
            results = store.search(question, top_k=3)

        for rank, r in enumerate(results, start=1):
            preview = r["content"][:100].replace("\n", " ")
            print(f"  top-{rank} score={r['score']:.3f} doc_id={r['metadata'].get('doc_id')} | {preview}...")

        answer = agent.answer(question, top_k=3)
        print(f"  Agent: {answer[:200]}...")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
