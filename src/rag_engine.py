"""
PULPNET RAG Engine
------------------
Transformer-based semantic search using:
  • SentenceTransformers (all-MiniLM-L6-v2 — BERT-based bi-encoder)
  • FAISS (Facebook AI Similarity Search) for fast approximate nearest-neighbour retrieval

Pipeline:
  1. Load IIT Kanpur knowledge base from JSON.
  2. Encode all document chunks into 384-dim L2-normalised embeddings.
  3. Build a FAISS IndexFlatIP (inner-product == cosine similarity on unit vectors).
  4. At query time: embed query → FAISS search → retrieve top-k docs → synthesise answer.
"""

import json
import os
from typing import Any, Dict, List, Tuple

import numpy as np

# ── Sentence Transformers (BERT-based bi-encoder) ─────────────────────────────
try:
    from sentence_transformers import SentenceTransformer
    HAS_ST = True
except ImportError:
    HAS_ST = False

# ── FAISS ─────────────────────────────────────────────────────────────────────
try:
    import faiss
    HAS_FAISS = True
except ImportError:
    HAS_FAISS = False

# ── Sklearn TF-IDF fallback ───────────────────────────────────────────────────
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False


class IITKChatbotRAG:
    """
    Retrieval-Augmented Generation (RAG) engine for IIT Kanpur campus queries.

    Embedding model : SentenceTransformers all-MiniLM-L6-v2 (BERT bi-encoder)
    Index backend   : FAISS IndexFlatIP (cosine similarity on L2-normalised vectors)
    Fallback        : TF-IDF cosine similarity (if faiss / sentence-transformers unavailable)
    """

    MODEL_NAME = "all-MiniLM-L6-v2"   # lightweight BERT-based bi-encoder

    def __init__(self, kb_path: str = "data/iitk_campus_kb.json"):
        self.kb_path = kb_path
        self.documents: List[Dict[str, Any]] = []

        # Transformer / FAISS state
        self.st_model: "SentenceTransformer | None" = None
        self.faiss_index: "faiss.IndexFlatIP | None" = None
        self.embeddings: "np.ndarray | None" = None

        # TF-IDF fallback state
        self.tfidf_vectorizer = None
        self.tfidf_matrix = None

        self._load_knowledge_base()
        self._build_index()

    # ── Data loading ──────────────────────────────────────────────────────────

    def _load_knowledge_base(self):
        if not os.path.exists(self.kb_path):
            from src.scraper import build_knowledge_base
            self.documents = build_knowledge_base(self.kb_path)
        else:
            with open(self.kb_path, "r", encoding="utf-8") as f:
                self.documents = json.load(f)

    # ── Index construction ────────────────────────────────────────────────────

    def _doc_texts(self) -> List[str]:
        """Combine title + category + content for each document."""
        return [
            f"{d['title']} [{d['category']}]: {d['content']}"
            for d in self.documents
        ]

    def _build_index(self):
        texts = self._doc_texts()

        # ── Primary: SentenceTransformers + FAISS ──────────────────────────
        if HAS_ST and HAS_FAISS:
            try:
                print(f"Loading SentenceTransformer model: {self.MODEL_NAME} ...")
                self.st_model = SentenceTransformer(self.MODEL_NAME)

                # Encode all documents → float32 matrix [N, dim]
                raw_embeddings = self.st_model.encode(
                    texts,
                    show_progress_bar=False,
                    convert_to_numpy=True,
                    normalize_embeddings=True,   # L2-normalise for cosine via IP
                )
                self.embeddings = raw_embeddings.astype("float32")

                # Build FAISS flat inner-product index (== cosine on unit vecs)
                dim = self.embeddings.shape[1]
                self.faiss_index = faiss.IndexFlatIP(dim)
                self.faiss_index.add(self.embeddings)

                print(
                    f"[OK] FAISS IndexFlatIP built -- {self.faiss_index.ntotal} vectors, dim={dim}"
                )
                return
            except Exception as exc:
                print(f"Warning: FAISS/SentenceTransformers init failed ({exc}). Falling back to TF-IDF.")

        # ── Fallback: TF-IDF ───────────────────────────────────────────────
        if HAS_SKLEARN:
            self.tfidf_vectorizer = TfidfVectorizer(
                stop_words="english", ngram_range=(1, 2)
            )
            self.tfidf_matrix = self.tfidf_vectorizer.fit_transform(texts)
            print("[WARN] Using TF-IDF fallback index (faiss-cpu or sentence-transformers not available).")
        else:
            print("[ERROR] No index backend available. Responses will be degraded.")

    # ── Retrieval ─────────────────────────────────────────────────────────────

    def retrieve(
        self,
        query: str,
        top_k: int = 3,
        category_filter: str = "All",
    ) -> List[Tuple[Dict[str, Any], float]]:
        """Return top_k (doc, score) pairs most relevant to *query*."""

        if not self.documents:
            return []

        # ── FAISS path ──────────────────────────────────────────────────────
        if self.st_model is not None and self.faiss_index is not None:
            # Embed & normalise query
            q_vec = self.st_model.encode(
                [query],
                convert_to_numpy=True,
                normalize_embeddings=True,
            ).astype("float32")

            # Search over ALL docs first, then apply category filter
            k = min(self.faiss_index.ntotal, max(top_k * 4, 10))
            scores, indices = self.faiss_index.search(q_vec, k)
            scores, indices = scores[0], indices[0]

            results: List[Tuple[Dict[str, Any], float]] = []
            for idx, score in zip(indices, scores):
                if idx < 0:
                    continue
                doc = self.documents[idx]
                if category_filter != "All" and doc.get("category") != category_filter:
                    continue
                results.append((doc, float(score)))
                if len(results) >= top_k:
                    break

            # If category filter left us empty, retry without filter
            if not results:
                for idx, score in zip(indices, scores):
                    if idx >= 0:
                        results.append((self.documents[idx], float(score)))
                    if len(results) >= top_k:
                        break

            return results

        # ── TF-IDF fallback path ────────────────────────────────────────────
        if self.tfidf_vectorizer is not None and self.tfidf_matrix is not None:
            filtered_indices = [
                i for i, d in enumerate(self.documents)
                if category_filter == "All" or d.get("category") == category_filter
            ] or list(range(len(self.documents)))

            q_vec = self.tfidf_vectorizer.transform([query])
            sub_matrix = self.tfidf_matrix[filtered_indices]
            sims = cosine_similarity(q_vec, sub_matrix).flatten()
            ranked = sorted(
                zip([self.documents[i] for i in filtered_indices], sims),
                key=lambda x: x[1],
                reverse=True,
            )
            return ranked[:top_k]

        # ── Last-resort word overlap ────────────────────────────────────────
        query_words = set(query.lower().split())
        scored = [
            (d, len(query_words & set(d["content"].lower().split())) / (len(query_words) + 1e-5))
            for d in self.documents
        ]
        return sorted(scored, key=lambda x: x[1], reverse=True)[:top_k]

    # ── Answer generation ─────────────────────────────────────────────────────

    def answer_query(
        self, query: str, category_filter: str = "All"
    ) -> Dict[str, Any]:
        """Retrieve context and synthesise a plain-language answer."""

        retrieved = self.retrieve(query, top_k=2, category_filter=category_filter)

        # Low-confidence / no-match guard
        if not retrieved or retrieved[0][1] < 0.15:
            return {
                "answer": (
                    "I couldn't find a direct match in the IIT Kanpur knowledge base for your query. "
                    "Try asking about academic programs, halls of residence (hostels), Vox Populi, "
                    "placements (SPO/ICS), library facilities, or Gymkhana festivals!"
                ),
                "confidence": 0.0,
                "sources": [],
                "primary_category": "General",
                "model_used": self._model_label(),
            }

        top_doc, top_score = retrieved[0]
        confidence_pct = min(round(top_score * 100, 1), 98.5)

        answer = (
            f"Based on official IIT Kanpur records for **{top_doc['title']}**:\n\n"
            f"{top_doc['content']}\n"
        )
        if len(retrieved) > 1 and retrieved[1][1] > 0.20:
            second_doc = retrieved[1][0]
            answer += (
                f"\n**Additional Context — {second_doc['title']}:**\n"
                f"{second_doc['content'][:380]}...\n"
            )

        sources = [
            {
                "title": d["title"],
                "category": d["category"],
                "url": d["source_url"],
                "score": min(round(s * 100, 1), 98.5),
                "snippet": d["content"][:220] + "...",
            }
            for d, s in retrieved
            if s > 0.15
        ]

        return {
            "answer": answer,
            "confidence": confidence_pct,
            "sources": sources,
            "primary_category": top_doc["category"],
            "model_used": self._model_label(),
        }

    def _model_label(self) -> str:
        if self.faiss_index is not None:
            return f"SentenceTransformers ({self.MODEL_NAME}) + FAISS IndexFlatIP"
        return "TF-IDF Cosine Similarity (fallback)"


# ── Quick self-test ───────────────────────────────────────────────────────────
if __name__ == "__main__":
    rag = IITKChatbotRAG()
    test_queries = [
        "Tell me about hostel life and halls of residence at IIT Kanpur",
        "What are the placement statistics at IITK?",
        "Explain Vox Populi and student media at IIT Kanpur",
    ]
    for q in test_queries:
        res = rag.answer_query(q)
        print(f"\nQ: {q}")
        print(f"   Model : {res['model_used']}")
        print(f"   Conf  : {res['confidence']}%")
        print(f"   Answer: {res['answer'][:200]}...")
