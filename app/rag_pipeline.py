"""
RAG pipeline for user-uploaded PDFs.

Design choice: a lightweight TF-IDF vector store (scikit-learn) instead of a
heavy embeddings model. This keeps the container small and deployable on
free-tier hosts (Render/Railway) with no GPU and no extra embedding API
calls/cost, while still satisfying "extract, chunk, embed, store in a
lightweight vector store, retrieve + blend with LLM output". Swap in
FAISS + sentence-transformers or an OpenAI/Gemini embeddings call in
`VectorStore` if you need semantic (not just lexical) retrieval.
"""
import re
import threading
from typing import List, Tuple, Optional

from pypdf import PdfReader
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.llm import chat as llm_chat


def extract_text_from_pdf(file_path: str) -> str:
    reader = PdfReader(file_path)
    pages = []
    for page in reader.pages:
        text = page.extract_text() or ""
        pages.append(text)
    return "\n".join(pages)


def chunk_text(text: str, chunk_size: int = 800, overlap: int = 120) -> List[str]:
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return []
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start = end - overlap
        if start < 0:
            start = 0
        if end >= len(text):
            break
    return [c.strip() for c in chunks if c.strip()]


class VectorStore:
    """A simple in-memory, thread-safe TF-IDF vector store."""

    def __init__(self):
        self.chunks: List[str] = []
        self.sources: List[str] = []
        self._vectorizer: Optional[TfidfVectorizer] = None
        self._matrix = None
        self._lock = threading.Lock()

    def add_document(self, filename: str, text: str) -> int:
        new_chunks = chunk_text(text)
        with self._lock:
            self.chunks.extend(new_chunks)
            self.sources.extend([filename] * len(new_chunks))
            self._rebuild_index()
        return len(new_chunks)

    def _rebuild_index(self):
        if not self.chunks:
            self._vectorizer = None
            self._matrix = None
            return
        self._vectorizer = TfidfVectorizer(stop_words="english")
        self._matrix = self._vectorizer.fit_transform(self.chunks)

    def is_empty(self) -> bool:
        return len(self.chunks) == 0

    def query(self, question: str, k: int = 4) -> List[Tuple[str, str, float]]:
        """Return top-k (chunk, source, score) tuples for a question."""
        if self.is_empty() or self._vectorizer is None:
            return []
        q_vec = self._vectorizer.transform([question])
        scores = cosine_similarity(q_vec, self._matrix).flatten()
        top_idx = scores.argsort()[::-1][:k]
        results = [(self.chunks[i], self.sources[i], float(scores[i])) for i in top_idx if scores[i] > 0]
        return results


# Single shared knowledge base for the whole app (simple, matches the
# "user uploads PDFs -> chatbot answers questions" use case).
store = VectorStore()


def ingest_pdf(file_path: str, filename: str) -> int:
    text = extract_text_from_pdf(file_path)
    if not text.strip():
        raise ValueError("No extractable text found in this PDF (it may be a scanned image).")
    return store.add_document(filename, text)


RAG_SYSTEM_PROMPT = (
    "You are a helpful assistant answering questions using ONLY the provided "
    "document excerpts. If the excerpts don't contain the answer, say you "
    "don't have that information in the uploaded documents. Be concise."
)


def rag_tool(query: str, history: list) -> str:
    """
    RAG Tool: Input -> query, Output -> retrieved answer (blends retrieved
    chunks with LLM output).
    """
    if store.is_empty():
        return (
            "I don't have any documents to search yet. Upload a PDF and I'll "
            "be able to answer questions about it."
        )

    results = store.query(query, k=4)
    if not results:
        return "I couldn't find anything relevant to that in the uploaded documents."

    context = "\n\n".join(f"[Source: {src}]\n{chunk}" for chunk, src, _ in results)
    prompt = f"Document excerpts:\n{context}\n\nQuestion: {query}"
    return llm_chat(RAG_SYSTEM_PROMPT, history, prompt)
