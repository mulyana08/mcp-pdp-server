#!/usr/bin/env python3
"""
Ingest Documents Script
=======================

Script untuk indexing dokumen PDF ke Pinecone vector database.
Jalankan script ini sekali untuk meng-upload dokumen ke Pinecone.

Usage:
    python scripts/ingest_documents.py
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.document.pdf_loader import load_uu_pdp
from src.document.chunker import chunk_uu_pdp
from src.rag.embeddings import EmbeddingService
from src.rag.pinecone_client import PineconeClient


def main():
    """Main function untuk ingesting documents."""
    print("=" * 60)
    print("📄 UU PDP Document Ingestion")
    print("=" * 60)

    # Step 1: Load PDF
    print("\n🔹 Step 1: Loading PDF...")
    try:
        text = load_uu_pdp()
        print(f"   ✅ Loaded PDF: {len(text):,} characters")
    except Exception as e:
        print(f"   ❌ Error loading PDF: {e}")
        return

    # Step 2: Chunk text
    print("\n🔹 Step 2: Chunking text...")
    try:
        chunks = chunk_uu_pdp(text, chunk_size=1000, chunk_overlap=200)
        print(f"   ✅ Created {len(chunks)} chunks")
    except Exception as e:
        print(f"   ❌ Error chunking: {e}")
        return

    # Step 3: Initialize services
    print("\n🔹 Step 3: Initializing services...")
    try:
        embedding_service = EmbeddingService()
        pinecone_client = PineconeClient()
        print("   ✅ Services initialized")
    except Exception as e:
        print(f"   ❌ Error initializing services: {e}")
        return

    # Step 4: Create Pinecone index
    print("\n🔹 Step 4: Creating/checking Pinecone index...")
    try:
        pinecone_client.create_index_if_not_exists(dimension=768)
    except Exception as e:
        print(f"   ❌ Error creating index: {e}")
        return

    # Step 5: Generate embeddings and upsert
    print("\n🔹 Step 5: Generating embeddings and uploading to Pinecone...")
    try:
        vectors = []

        for i, chunk in enumerate(chunks):
            # Generate embedding
            embedding = embedding_service.embed_text(chunk["text"])

            # Prepare vector
            vector = {
                "id": f"uu-pdp-chunk-{i}",
                "values": embedding,
                "metadata": {
                    "text": chunk["text"],
                    **chunk["metadata"],
                },
            }
            vectors.append(vector)

            # Progress
            if (i + 1) % 10 == 0:
                print(f"   📊 Embedded {i + 1}/{len(chunks)} chunks...")

        print(f"   ✅ Generated {len(vectors)} embeddings")

        # Upsert to Pinecone
        print("\n🔹 Step 6: Upserting vectors to Pinecone...")
        result = pinecone_client.upsert_vectors(vectors, batch_size=50)
        print(f"   ✅ Upserted {result['upserted_count']} vectors")

    except Exception as e:
        print(f"   ❌ Error during embedding/upsert: {e}")
        return

    # Step 7: Verify
    print("\n🔹 Step 7: Verifying...")
    try:
        stats = pinecone_client.get_stats()
        print(f"   📊 Total vectors in index: {stats.get('total_vector_count', 0)}")
    except Exception as e:
        print(f"   ⚠️ Could not verify: {e}")

    print("\n" + "=" * 60)
    print("✅ Document ingestion completed successfully!")
    print("=" * 60)
    print("\nAnda sekarang bisa menjalankan MCP server dengan:")
    print("  python -m src.server")


if __name__ == "__main__":
    main()
