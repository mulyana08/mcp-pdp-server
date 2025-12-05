"""
MCP PDP Server
==============

MCP Server untuk menjawab pertanyaan tentang UU Perlindungan Data Pribadi
No 27 Tahun 2022.
"""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

# Load environment variables
load_dotenv()

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.rag.retriever import RAGRetriever

# Initialize FastMCP server
mcp = FastMCP(
    "PDP-Assistant",
)

# Global retriever (lazy initialized)
_retriever = None


def get_retriever() -> RAGRetriever:
    """Get or create RAGRetriever instance."""
    global _retriever
    if _retriever is None:
        _retriever = RAGRetriever()
    return _retriever


@mcp.tool()
async def tanya_pdp(pertanyaan: str) -> str:
    """
    Menjawab pertanyaan seputar UU Perlindungan Data Pribadi No 27 Tahun 2022.

    Gunakan tool ini untuk bertanya tentang:
    - Definisi dan konsep dalam UU PDP
    - Hak-hak subjek data pribadi
    - Kewajiban pengendali dan prosesor data
    - Sanksi dan ketentuan pidana
    - Dan topik lainnya terkait perlindungan data pribadi

    Args:
        pertanyaan: Pertanyaan tentang UU PDP dalam bahasa Indonesia

    Returns:
        Jawaban berdasarkan UU PDP beserta referensi pasal
    """
    retriever = get_retriever()
    result = retriever.answer(pertanyaan)

    # Format response
    response = result["answer"]

    # Add sources
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


@mcp.tool()
async def cari_pasal(nomor_pasal: int) -> str:
    """
    Mencari dan menampilkan isi pasal tertentu dalam UU PDP.

    UU PDP terdiri dari 76 pasal (Pasal 1 sampai Pasal 76).

    Args:
        nomor_pasal: Nomor pasal yang dicari (1-76)

    Returns:
        Isi lengkap pasal yang dimaksud
    """
    if nomor_pasal < 1 or nomor_pasal > 76:
        return f"Nomor pasal harus antara 1-76. Anda memasukkan: {nomor_pasal}"

    retriever = get_retriever()
    query = f"Apa isi lengkap Pasal {nomor_pasal} UU Perlindungan Data Pribadi?"

    result = retriever.answer(query, top_k=3)

    return f"📜 Pasal {nomor_pasal} UU PDP:\n\n{result['answer']}"


@mcp.tool()
async def ringkasan_bab(nomor_bab: str) -> str:
    """
    Memberikan ringkasan dari bab tertentu dalam UU PDP.

    UU PDP terdiri dari 16 BAB:
    - BAB I: Ketentuan Umum
    - BAB II: Asas
    - BAB III: Jenis Data Pribadi
    - BAB IV: Hak Subjek Data Pribadi
    - BAB V: Pemrosesan Data Pribadi
    - BAB VI: Kewajiban Pengendali & Prosesor
    - BAB VII: Transfer Data Pribadi
    - BAB VIII: Sanksi Administratif
    - BAB IX: Kelembagaan
    - BAB X: Kerjasama Internasional
    - BAB XI: Partisipasi Masyarakat
    - BAB XII: Penyelesaian Sengketa
    - BAB XIII: Larangan Penggunaan Data
    - BAB XIV: Ketentuan Pidana
    - BAB XV: Ketentuan Peralihan
    - BAB XVI: Ketentuan Penutup

    Args:
        nomor_bab: Nomor bab (1-16 atau I-XVI)

    Returns:
        Ringkasan isi bab tersebut
    """
    # Convert angka ke romawi
    romawi_map = {
        "1": "I", "2": "II", "3": "III", "4": "IV", "5": "V",
        "6": "VI", "7": "VII", "8": "VIII", "9": "IX", "10": "X",
        "11": "XI", "12": "XII", "13": "XIII", "14": "XIV", "15": "XV",
        "16": "XVI",
    }

    bab_romawi = romawi_map.get(str(nomor_bab), str(nomor_bab).upper())

    valid_babs = list(romawi_map.values())
    if bab_romawi not in valid_babs:
        return f"Nomor BAB tidak valid. Gunakan 1-16 atau I-XVI. Anda memasukkan: {nomor_bab}"

    retriever = get_retriever()
    query = f"Apa saja yang diatur dalam BAB {bab_romawi} UU Perlindungan Data Pribadi? Berikan ringkasan lengkap."

    result = retriever.answer(query, top_k=5)

    return f"📖 Ringkasan BAB {bab_romawi} UU PDP:\n\n{result['answer']}"


@mcp.tool()
async def info_uu_pdp() -> str:
    """
    Menampilkan informasi umum dan struktur UU Perlindungan Data Pribadi.

    Gunakan tool ini untuk melihat gambaran umum UU PDP termasuk
    daftar semua BAB dan jumlah pasal.

    Returns:
        Informasi struktur lengkap UU PDP
    """
    return """
📜 UNDANG-UNDANG NOMOR 27 TAHUN 2022
   TENTANG PERLINDUNGAN DATA PRIBADI

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📑 STRUKTUR UU PDP:

   BAB I    - Ketentuan Umum (Pasal 1-2)
   BAB II   - Asas (Pasal 3)
   BAB III  - Jenis Data Pribadi (Pasal 4)
   BAB IV   - Hak Subjek Data Pribadi (Pasal 5-15)
   BAB V    - Pemrosesan Data Pribadi (Pasal 16-19)
   BAB VI   - Kewajiban Pengendali & Prosesor (Pasal 20-45)
   BAB VII  - Transfer Data Pribadi (Pasal 46-49)
   BAB VIII - Sanksi Administratif (Pasal 50-52)
   BAB IX   - Kelembagaan (Pasal 53-62)
   BAB X    - Kerjasama Internasional (Pasal 63)
   BAB XI   - Partisipasi Masyarakat (Pasal 64)
   BAB XII  - Penyelesaian Sengketa & Hukum Acara (Pasal 65-66)
   BAB XIII - Larangan Penggunaan Data Pribadi (Pasal 67)
   BAB XIV  - Ketentuan Pidana (Pasal 68-73)
   BAB XV   - Ketentuan Peralihan (Pasal 74)
   BAB XVI  - Ketentuan Penutup (Pasal 75-76)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 RINGKASAN:
   • Total BAB: 16
   • Total Pasal: 76
   • Disahkan: 17 Oktober 2022
   • Berlaku: 17 Oktober 2024 (2 tahun transisi)

🔧 TOOLS TERSEDIA:
   • tanya_pdp - Tanya jawab tentang UU PDP
   • cari_pasal - Cari isi pasal tertentu
   • ringkasan_bab - Ringkasan per bab
   • info_uu_pdp - Informasi struktur (ini)
"""


def main():
    """Run the MCP server."""
    host = os.getenv("MCP_HOST", "0.0.0.0")
    port = int(os.getenv("MCP_PORT", 8000))

    print(f"🚀 Starting MCP PDP Server on {host}:{port}")
    print(f"📚 UU Perlindungan Data Pribadi No 27 Tahun 2022")
    print(f"🔧 Tools: tanya_pdp, cari_pasal, ringkasan_bab, info_uu_pdp")

    mcp.run()


if __name__ == "__main__":
    main()
