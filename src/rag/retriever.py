"""
RAG Retriever Module
====================

Module untuk retrieval dan generation menggunakan RAG pattern.
"""

import os
from typing import Optional

import google.generativeai as genai
from dotenv import load_dotenv

from .embeddings import EmbeddingService
from .pinecone_client import PineconeClient

# Load environment variables
load_dotenv()


class RAGRetriever:
    """RAG Retriever untuk menjawab pertanyaan berdasarkan dokumen."""

    def __init__(
        self,
        embedding_service: Optional[EmbeddingService] = None,
        pinecone_client: Optional[PineconeClient] = None,
        model: Optional[str] = None,
        top_k: int = 5,
    ):
        """
        Initialize RAG Retriever.

        Args:
            embedding_service: Service untuk embeddings
            pinecone_client: Client untuk Pinecone
            model: Model Gemini untuk generation
            top_k: Jumlah dokumen yang di-retrieve
        """
        self.embedding_service = embedding_service or EmbeddingService()
        self.pinecone_client = pinecone_client or PineconeClient()
        self.model = model or os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
        self.top_k = int(os.getenv("TOP_K_RESULTS", top_k))

        # Configure Gemini for generation
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        self.llm = genai.GenerativeModel(self.model)

    def retrieve(self, query: str, top_k: Optional[int] = None) -> list[dict]:
        """
        Retrieve relevant documents untuk query.

        Args:
            query: User query
            top_k: Override jumlah dokumen

        Returns:
            List of relevant documents dengan score
        """
        k = top_k or self.top_k

        # Generate query embedding
        query_embedding = self.embedding_service.embed_query(query)

        # Query Pinecone
        results = self.pinecone_client.query(
            vector=query_embedding,
            top_k=k,
            include_metadata=True,
        )

        return results

    def generate_context(self, documents: list[dict]) -> str:
        """
        Generate context string dari retrieved documents.

        Args:
            documents: List of retrieved documents

        Returns:
            Formatted context string
        """
        context_parts = []

        for i, doc in enumerate(documents, 1):
            metadata = doc.get("metadata", {})
            text = metadata.get("text", "")

            # Format dengan metadata
            pasal = metadata.get("pasal", "")
            bab = metadata.get("bab", "")

            header = f"[Dokumen {i}]"
            if bab:
                header += f" BAB {bab}"
            if pasal:
                header += f" Pasal {pasal}"

            context_parts.append(f"{header}\n{text}")

        return "\n\n---\n\n".join(context_parts)

    def answer(self, query: str, top_k: Optional[int] = None) -> dict:
        """
        Jawab pertanyaan menggunakan RAG.

        Args:
            query: User query
            top_k: Override jumlah dokumen

        Returns:
            Dict dengan answer dan sources
        """
        # Retrieve relevant documents
        documents = self.retrieve(query, top_k)

        if not documents:
            return {
                "answer": "Maaf, saya tidak menemukan informasi yang relevan dalam UU PDP.",
                "sources": [],
                "context": "",
            }

        # Generate context
        context = self.generate_context(documents)

        # Create prompt
        prompt = self._create_prompt(query, context)

        # Generate answer
        response = self.llm.generate_content(prompt)
        answer = response.text

        # Extract sources
        sources = self._extract_sources(documents)

        return {
            "answer": answer,
            "sources": sources,
            "context": context,
        }

    def _create_prompt(self, query: str, context: str) -> str:
        """
        Create prompt untuk LLM.

        Args:
            query: User query
            context: Retrieved context

        Returns:
            Formatted prompt
        """
        return f"""Anda adalah asisten ahli hukum yang membantu menjawab pertanyaan tentang UU Perlindungan Data Pribadi (UU No. 27 Tahun 2022).

Gunakan HANYA informasi dari konteks berikut untuk menjawab pertanyaan. Jika informasi tidak ada dalam konteks, katakan bahwa Anda tidak menemukan informasi tersebut dalam UU PDP.

KONTEKS:
{context}

PERTANYAAN: {query}

INSTRUKSI:
1. Jawab dengan bahasa Indonesia yang jelas dan mudah dipahami
2. Sebutkan pasal yang relevan jika ada
3. Jika pertanyaan tidak bisa dijawab dari konteks, jelaskan dengan sopan
4. Berikan jawaban yang akurat berdasarkan UU PDP

JAWABAN:"""

    def _extract_sources(self, documents: list[dict]) -> list[dict]:
        """
        Extract source references dari documents.

        Args:
            documents: Retrieved documents

        Returns:
            List of source references
        """
        sources = []

        for doc in documents:
            metadata = doc.get("metadata", {})
            source = {
                "score": doc.get("score", 0),
                "pasal": metadata.get("pasal", ""),
                "bab": metadata.get("bab", ""),
            }
            sources.append(source)

        return sources


def get_rag_retriever() -> RAGRetriever:
    """
    Factory function untuk mendapatkan RAGRetriever instance.

    Returns:
        RAGRetriever instance
    """
    return RAGRetriever()


if __name__ == "__main__":
    # Test RAG retrieval
    try:
        retriever = RAGRetriever()

        # Test query
        query = "Apa itu data pribadi menurut UU PDP?"
        print(f"🔍 Query: {query}\n")

        result = retriever.answer(query)

        print(f"📝 Answer:\n{result['answer']}\n")
        print(f"📚 Sources: {result['sources']}")

    except Exception as e:
        print(f"❌ Error: {e}")
