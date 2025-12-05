"""
PDP Tools Module
================

MCP Tools untuk menjawab pertanyaan tentang UU Perlindungan Data Pribadi.
"""

from typing import Optional

from ..rag.retriever import RAGRetriever


# Global retriever instance
_retriever: Optional[RAGRetriever] = None


def get_retriever() -> RAGRetriever:
    """Get or create RAGRetriever instance."""
    global _retriever
    if _retriever is None:
        _retriever = RAGRetriever()
    return _retriever


async def tanya_pdp(pertanyaan: str) -> str:
    """
    Menjawab pertanyaan seputar UU Perlindungan Data Pribadi No 27 Tahun 2022.

    Args:
        pertanyaan: Pertanyaan tentang UU PDP

    Returns:
        Jawaban berdasarkan UU PDP
    """
    retriever = get_retriever()
    result = retriever.answer(pertanyaan)

    # Format response
    response = result["answer"]

    # Add sources if available
    sources = result.get("sources", [])
    if sources:
        relevant_sources = [s for s in sources if s.get("pasal")]
        if relevant_sources:
            pasal_refs = set()
            for s in relevant_sources:
                if s.get("pasal"):
                    ref = f"Pasal {s['pasal']}"
                    if s.get("bab"):
                        ref = f"BAB {s['bab']}, {ref}"
                    pasal_refs.add(ref)

            if pasal_refs:
                response += f"\n\n📚 Referensi: {', '.join(sorted(pasal_refs))}"

    return response


async def cari_pasal(nomor_pasal: int) -> str:
    """
    Mencari isi pasal tertentu dalam UU Perlindungan Data Pribadi.

    Args:
        nomor_pasal: Nomor pasal yang dicari (1-76)

    Returns:
        Isi pasal yang dimaksud
    """
    retriever = get_retriever()

    # Query spesifik untuk pasal
    query = f"Pasal {nomor_pasal} UU Perlindungan Data Pribadi"

    result = retriever.answer(query, top_k=3)

    # Check if pasal found in sources
    sources = result.get("sources", [])
    pasal_found = any(s.get("pasal") == str(nomor_pasal) for s in sources)

    if not pasal_found:
        return f"Maaf, Pasal {nomor_pasal} tidak ditemukan atau mungkin di luar jangkauan UU PDP (Pasal 1-76)."

    return result["answer"]


async def ringkasan_bab(nomor_bab: str) -> str:
    """
    Memberikan ringkasan dari bab tertentu dalam UU Perlindungan Data Pribadi.

    Args:
        nomor_bab: Nomor bab dalam format Romawi (I, II, III, dst) atau angka (1, 2, 3)

    Returns:
        Ringkasan bab yang dimaksud
    """
    # Convert angka ke romawi jika perlu
    romawi_map = {
        "1": "I", "2": "II", "3": "III", "4": "IV", "5": "V",
        "6": "VI", "7": "VII", "8": "VIII", "9": "IX", "10": "X",
        "11": "XI", "12": "XII", "13": "XIII", "14": "XIV", "15": "XV",
        "16": "XVI",
    }

    bab_romawi = romawi_map.get(str(nomor_bab), str(nomor_bab).upper())

    retriever = get_retriever()

    # Query untuk ringkasan bab
    query = f"Ringkasan BAB {bab_romawi} UU Perlindungan Data Pribadi. Apa saja yang diatur dalam BAB {bab_romawi}?"

    result = retriever.answer(query, top_k=5)

    # Check if bab found
    sources = result.get("sources", [])
    bab_found = any(s.get("bab") == bab_romawi for s in sources)

    if not bab_found:
        return f"Maaf, BAB {bab_romawi} tidak ditemukan. UU PDP terdiri dari BAB I sampai BAB XVI."

    return f"📖 Ringkasan BAB {bab_romawi}:\n\n{result['answer']}"


# Info tentang struktur UU PDP
UU_PDP_STRUKTUR = """
📜 UNDANG-UNDANG NO. 27 TAHUN 2022
   TENTANG PERLINDUNGAN DATA PRIBADI

📑 STRUKTUR:
   BAB I    - Ketentuan Umum
   BAB II   - Asas
   BAB III  - Jenis Data Pribadi
   BAB IV   - Hak Subjek Data Pribadi
   BAB V    - Pemrosesan Data Pribadi
   BAB VI   - Kewajiban Pengendali & Prosesor Data Pribadi
   BAB VII  - Transfer Data Pribadi
   BAB VIII - Sanksi Administratif
   BAB IX   - Kelembagaan
   BAB X    - Kerjasama Internasional
   BAB XI   - Partisipasi Masyarakat
   BAB XII  - Penyelesaian Sengketa & Hukum Acara
   BAB XIII - Larangan dalam Penggunaan Data Pribadi
   BAB XIV  - Ketentuan Pidana
   BAB XV   - Ketentuan Peralihan
   BAB XVI  - Ketentuan Penutup

📄 Total: 76 Pasal
"""


async def info_uu_pdp() -> str:
    """
    Memberikan informasi umum tentang struktur UU Perlindungan Data Pribadi.

    Returns:
        Informasi struktur UU PDP
    """
    return UU_PDP_STRUKTUR
