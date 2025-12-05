#!/usr/bin/env python3
"""
Test RAG Script
===============

Script untuk testing RAG pipeline secara lokal.

Usage:
    python scripts/test_rag.py
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.rag.retriever import RAGRetriever


def test_queries():
    """Test berbagai query untuk RAG."""
    queries = [
        "Apa definisi data pribadi menurut UU PDP?",
        "Apa saja hak-hak subjek data pribadi?",
        "Bagaimana sanksi pelanggaran data pribadi?",
        "Apa itu pengendali data pribadi?",
        "Apa yang dimaksud dengan pemrosesan data pribadi?",
    ]
    return queries


def main():
    print("=" * 60)
    print("🧪 Testing RAG Pipeline")
    print("=" * 60)

    # Initialize retriever
    print("\n🔹 Initializing RAG Retriever...")
    try:
        retriever = RAGRetriever()
        print("   ✅ Retriever initialized")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        print("\n⚠️ Make sure you have:")
        print("   1. Set GOOGLE_API_KEY in .env")
        print("   2. Set PINECONE_API_KEY in .env")
        print("   3. Run 'python scripts/ingest_documents.py' first")
        return

    # Get test queries
    queries = test_queries()

    # Interactive mode or batch mode
    if len(sys.argv) > 1:
        # Use command line argument as query
        query = " ".join(sys.argv[1:])
        queries = [query]

    # Test each query
    for i, query in enumerate(queries, 1):
        print(f"\n{'=' * 60}")
        print(f"🔍 Query {i}: {query}")
        print("=" * 60)

        try:
            result = retriever.answer(query)

            print(f"\n📝 Answer:\n{result['answer']}")

            if result.get("sources"):
                print(f"\n📚 Sources:")
                for j, source in enumerate(result["sources"], 1):
                    pasal = source.get("pasal", "N/A")
                    bab = source.get("bab", "N/A")
                    score = source.get("score", 0)
                    print(f"   {j}. BAB {bab}, Pasal {pasal} (score: {score:.3f})")

        except Exception as e:
            print(f"\n❌ Error: {e}")

        print()

    # Interactive mode
    print("\n" + "=" * 60)
    print("💬 Interactive Mode (ketik 'exit' untuk keluar)")
    print("=" * 60)

    while True:
        try:
            query = input("\n🔍 Pertanyaan: ").strip()

            if query.lower() in ["exit", "quit", "q"]:
                print("👋 Bye!")
                break

            if not query:
                continue

            result = retriever.answer(query)
            print(f"\n📝 Jawaban:\n{result['answer']}")

            if result.get("sources"):
                print(f"\n📚 Referensi:")
                for j, source in enumerate(result["sources"], 1):
                    pasal = source.get("pasal", "N/A")
                    bab = source.get("bab", "N/A")
                    print(f"   {j}. BAB {bab}, Pasal {pasal}")

        except KeyboardInterrupt:
            print("\n👋 Bye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    main()
