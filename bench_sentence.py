from __future__ import annotations

import re
import os
from pathlib import Path

from dotenv import load_dotenv

from src import (
    Document,
    EmbeddingStore,
    GeminiEmbedder,
    LocalEmbedder,
    OpenAIEmbedder,
    SentenceChunker,
    _mock_embed,
)

DATA_DIR = Path("data/return-refund-policy")
OUTPUT_PATH = Path("ket_qua_benchmark_sentence.txt")
MAX_SENTENCES_PER_CHUNK = 8

QUERIES = [
    {
        "question": "Người mua nào đủ điều kiện Trả hàng COM, hạn mức của ShopeeVIP là bao nhiêu và trường hợp nào bị loại trừ?",
        "filter": {"audience": "buyer", "doc_id": "shopee-chinh-sach-tra-hang-nguoi-mua"},
        "gold_doc_ids": ["shopee-chinh-sach-tra-hang-nguoi-mua"],
    },
    {
        "question": "Người bán phải phản hồi yêu cầu Trả hàng/Hoàn tiền trong bao lâu, và điều gì xảy ra nếu không phản hồi đúng hạn?",
        "filter": {"audience": "seller", "doc_id": "shopee-chinh-sach-tra-hang-nguoi-ban"},
        "gold_doc_ids": ["shopee-chinh-sach-tra-hang-nguoi-ban"],
    },
    {
        "question": "Theo chính sách dành cho người bán, trường hợp nào người bán chịu chi phí vận chuyển chiều hoàn trả và trường hợp nào không phải chịu?",
        "filter": {"audience": "seller", "doc_id": "shopee-chinh-sach-tra-hang-nguoi-ban"},
        "gold_doc_ids": ["shopee-chinh-sach-tra-hang-nguoi-ban"],
    },
    {
        "question": "Nếu người mua tự sắp xếp trả hàng, chính sách hoàn chi phí khác nhau thế nào giữa sản phẩm Shopee Mall và sản phẩm không thuộc Shopee Mall?",
        "filter": {"audience": "buyer", "doc_id": "shopee-chinh-sach-tra-hang-nguoi-mua"},
        "gold_doc_ids": ["shopee-chinh-sach-tra-hang-nguoi-mua"],
    },
    {
        "question": "Nếu người bán đề xuất Hoàn tiền ngay, mức hoàn tối thiểu là bao nhiêu và người mua có lựa chọn gì nếu không đồng ý?",
        "filter": None,
        "gold_doc_ids": ["shopee-chinh-sach-tra-hang-nguoi-mua", "shopee-chinh-sach-tra-hang-nguoi-ban"],
    },
]


def parse_front_matter(text: str) -> tuple[dict[str, str], str]:
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n?(.*)$", text, re.DOTALL)
    if not match:
        return {}, text
    metadata: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        metadata[key.strip()] = value.strip().strip('"')
    return metadata, match.group(2).strip()


def load_sentence_documents() -> list[Document]:
    chunker = SentenceChunker(max_sentences_per_chunk=MAX_SENTENCES_PER_CHUNK)
    documents: list[Document] = []
    for path in sorted(DATA_DIR.glob("*.md")):
        metadata, content = parse_front_matter(path.read_text(encoding="utf-8"))
        metadata["doc_id"] = path.stem
        metadata["file_path"] = str(path).replace("\\", "/")
        chunks = chunker.chunk(content)
        for index, chunk in enumerate(chunks):
            documents.append(Document(id=f"{path.stem}#{index}", content=chunk, metadata=dict(metadata)))
    return documents


def load_embedder():
    load_dotenv(override=False)
    provider = os.getenv("EMBEDDING_PROVIDER", "mock").strip().lower()
    if provider == "gemini":
        return GeminiEmbedder(model_name=os.getenv("GEMINI_EMBEDDING_MODEL", "gemini-embedding-001"))
    if provider == "openai":
        return OpenAIEmbedder(model_name=os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"))
    if provider == "local":
        return LocalEmbedder(model_name=os.getenv("LOCAL_EMBEDDING_MODEL", "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"))
    return _mock_embed


class BatchedEmbedder:
    def __init__(self, backend, documents: list[Document], batch_size: int = 50) -> None:
        self.backend = backend
        self._backend_name = getattr(backend, "_backend_name", backend.__class__.__name__)
        self.vectors: dict[str, list[float]] = {}
        contents = [document.content for document in documents]
        if isinstance(backend, GeminiEmbedder):
            for start in range(0, len(contents), batch_size):
                batch = contents[start : start + batch_size]
                response = backend.client.models.embed_content(model=backend.model_name, contents=batch)
                self.vectors.update(zip(batch, [embedding.values for embedding in response.embeddings]))
        else:
            for content in contents:
                self.vectors[content] = backend(content)

    def __call__(self, text: str) -> list[float]:
        if text not in self.vectors:
            self.vectors[text] = self.backend(text)
        return self.vectors[text]


def main() -> None:
    documents = load_sentence_documents()
    embedder = BatchedEmbedder(load_embedder(), documents)
    store = EmbeddingStore(collection_name="sentence_strategy", embedding_fn=embedder)
    store.add_documents(documents)
    lines = [
        "SentenceChunker benchmark",
        f"max_sentences_per_chunk={MAX_SENTENCES_PER_CHUNK}",
        f"embedding_backend={getattr(embedder, '_backend_name', embedder.__class__.__name__)}",
        f"documents={len(documents)}",
        "Scores come from the embedding backend shown above; inspect gold-answer coverage, not score alone.",
        "",
    ]
    for number, item in enumerate(QUERIES, start=1):
        results = store.search_with_filter(item["question"], top_k=3, metadata_filter=item["filter"])
        lines.append(f"[{number}] {item['question']}")
        lines.append(f"  filter={item['filter']}")
        lines.append(f"  gold_doc_ids={item['gold_doc_ids']}")
        for rank, result in enumerate(results, start=1):
            preview = " ".join(result["content"].split())[:240]
            lines.append(f"  top-{rank} score={result['score']:.6f} id={result['id']} doc_id={result['metadata']['doc_id']}")
            lines.append(f"    {preview}")
        lines.append("")

    OUTPUT_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(f"Loaded {len(documents)} sentence chunks")
    print(f"Wrote {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
