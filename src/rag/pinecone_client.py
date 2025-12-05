"""
Pinecone Client Module
======================

Module untuk operasi vector database menggunakan Pinecone.
"""

import os
from typing import Optional

from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec

# Load environment variables
load_dotenv()


class PineconeClient:
    """Client untuk operasi Pinecone vector database."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        index_name: Optional[str] = None,
    ):
        """
        Initialize Pinecone Client.

        Args:
            api_key: Pinecone API key
            index_name: Nama index Pinecone
        """
        self.api_key = api_key or os.getenv("PINECONE_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Pinecone API Key tidak ditemukan. "
                "Set PINECONE_API_KEY di environment."
            )

        self.index_name = index_name or os.getenv("PINECONE_INDEX_NAME", "uu-pdp-27-2022")

        # Initialize Pinecone
        self.pc = Pinecone(api_key=self.api_key)
        self._index = None

    def create_index_if_not_exists(self, dimension: int = 768) -> None:
        """
        Buat index jika belum ada.

        Args:
            dimension: Dimensi embedding vector
        """
        existing_indexes = [idx.name for idx in self.pc.list_indexes()]

        if self.index_name not in existing_indexes:
            print(f"📦 Creating index '{self.index_name}'...")
            self.pc.create_index(
                name=self.index_name,
                dimension=dimension,
                metric="cosine",
                spec=ServerlessSpec(
                    cloud="aws",
                    region="us-east-1",
                ),
            )
            print(f"✅ Index '{self.index_name}' created!")
        else:
            print(f"✅ Index '{self.index_name}' already exists.")

    @property
    def index(self):
        """Get Pinecone index instance."""
        if self._index is None:
            self._index = self.pc.Index(self.index_name)
        return self._index

    def upsert_vectors(
        self,
        vectors: list[dict],
        namespace: str = "",
        batch_size: int = 100,
    ) -> dict:
        """
        Upsert vectors ke Pinecone.

        Args:
            vectors: List of dicts dengan keys: id, values, metadata
            namespace: Namespace untuk vectors
            batch_size: Ukuran batch per upsert

        Returns:
            Upsert stats
        """
        total_upserted = 0

        for i in range(0, len(vectors), batch_size):
            batch = vectors[i : i + batch_size]

            # Format untuk Pinecone
            records = [
                {
                    "id": v["id"],
                    "values": v["values"],
                    "metadata": v.get("metadata", {}),
                }
                for v in batch
            ]

            self.index.upsert(vectors=records, namespace=namespace)
            total_upserted += len(batch)
            print(f"  Upserted {total_upserted}/{len(vectors)} vectors")

        return {"upserted_count": total_upserted}

    def query(
        self,
        vector: list[float],
        top_k: int = 5,
        namespace: str = "",
        include_metadata: bool = True,
    ) -> list[dict]:
        """
        Query vectors dari Pinecone.

        Args:
            vector: Query embedding vector
            top_k: Jumlah hasil yang dikembalikan
            namespace: Namespace untuk query
            include_metadata: Include metadata dalam hasil

        Returns:
            List of matches dengan score dan metadata
        """
        results = self.index.query(
            vector=vector,
            top_k=top_k,
            namespace=namespace,
            include_metadata=include_metadata,
        )

        matches = []
        for match in results.matches:
            matches.append({
                "id": match.id,
                "score": match.score,
                "metadata": match.metadata if include_metadata else {},
            })

        return matches

    def delete_all(self, namespace: str = "") -> None:
        """
        Hapus semua vectors dalam namespace.

        Args:
            namespace: Namespace yang akan dihapus
        """
        self.index.delete(delete_all=True, namespace=namespace)
        print(f"🗑️ Deleted all vectors in namespace '{namespace}'")

    def get_stats(self) -> dict:
        """
        Get statistics dari index.

        Returns:
            Index statistics
        """
        return self.index.describe_index_stats()


def get_pinecone_client() -> PineconeClient:
    """
    Factory function untuk mendapatkan PineconeClient instance.

    Returns:
        PineconeClient instance
    """
    return PineconeClient()


if __name__ == "__main__":
    # Test Pinecone connection
    try:
        client = PineconeClient()

        # Check/create index
        client.create_index_if_not_exists(dimension=768)

        # Get stats
        stats = client.get_stats()
        print(f"\n📊 Index Stats:")
        print(f"   Total vectors: {stats.get('total_vector_count', 0)}")
        print(f"   Dimension: {stats.get('dimension', 'N/A')}")

    except Exception as e:
        print(f"❌ Error: {e}")
