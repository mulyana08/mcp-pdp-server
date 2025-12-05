"""
Embeddings Module
=================

Module untuk generate embeddings menggunakan Google Generative AI.
"""

import os
from typing import Optional

import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class EmbeddingService:
    """Service untuk generate embeddings menggunakan Google Gemini."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "text-embedding-004",
    ):
        """
        Initialize Embedding Service.

        Args:
            api_key: Google API key (optional, akan ambil dari env jika tidak ada)
            model: Model embedding yang digunakan
        """
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Google API Key tidak ditemukan. "
                "Set GOOGLE_API_KEY di environment atau pass sebagai parameter."
            )

        self.model = model

        # Configure Google AI
        genai.configure(api_key=self.api_key)

    def embed_text(self, text: str) -> list[float]:
        """
        Generate embedding untuk single text.

        Args:
            text: Teks yang akan di-embed

        Returns:
            List of floats (embedding vector)
        """
        result = genai.embed_content(
            model=f"models/{self.model}",
            content=text,
            task_type="retrieval_document",
        )
        return result["embedding"]

    def embed_query(self, query: str) -> list[float]:
        """
        Generate embedding untuk query (untuk retrieval).

        Args:
            query: Query text

        Returns:
            List of floats (embedding vector)
        """
        result = genai.embed_content(
            model=f"models/{self.model}",
            content=query,
            task_type="retrieval_query",
        )
        return result["embedding"]

    def embed_batch(self, texts: list[str], batch_size: int = 100) -> list[list[float]]:
        """
        Generate embeddings untuk batch of texts.

        Args:
            texts: List of texts
            batch_size: Ukuran batch per request

        Returns:
            List of embedding vectors
        """
        embeddings = []

        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]

            # Process batch
            for text in batch:
                embedding = self.embed_text(text)
                embeddings.append(embedding)

            print(f"  Processed {min(i + batch_size, len(texts))}/{len(texts)} texts")

        return embeddings

    @property
    def dimension(self) -> int:
        """
        Get dimensi dari embedding model.

        Returns:
            Dimensi embedding (768 untuk text-embedding-004)
        """
        # text-embedding-004 menghasilkan 768 dimensi
        return 768


def get_embedding_service() -> EmbeddingService:
    """
    Factory function untuk mendapatkan EmbeddingService instance.

    Returns:
        EmbeddingService instance
    """
    return EmbeddingService()


if __name__ == "__main__":
    # Test embedding
    try:
        service = EmbeddingService()

        # Test single embedding
        test_text = "Apa itu data pribadi menurut UU PDP?"
        embedding = service.embed_query(test_text)

        print(f"✅ Embedding berhasil!")
        print(f"📊 Dimensi: {len(embedding)}")
        print(f"📄 Text: {test_text}")
        print(f"🔢 Preview embedding (5 nilai pertama): {embedding[:5]}")

    except Exception as e:
        print(f"❌ Error: {e}")
