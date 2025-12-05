"""
Text Chunker Module
===================

Module untuk membagi teks dokumen menjadi chunks yang sesuai untuk embedding.
"""

import re
from typing import Optional

from langchain_text_splitters import RecursiveCharacterTextSplitter


class TextChunker:
    """Membagi teks menjadi chunks untuk vector embedding."""

    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        separators: Optional[list[str]] = None,
    ):
        """
        Initialize Text Chunker.

        Args:
            chunk_size: Ukuran maksimum setiap chunk (dalam karakter)
            chunk_overlap: Overlap antar chunk untuk menjaga konteks
            separators: List separator untuk splitting (default: paragraph, newline, space)
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

        # Separators khusus untuk dokumen UU Indonesia
        self.separators = separators or [
            "\n\nBAB ",      # Bab baru
            "\n\nPasal ",    # Pasal baru
            "\n\nBagian ",   # Bagian baru
            "\n\nParagraf ", # Paragraf baru
            "\n\n",          # Paragraf
            "\n",            # Baris baru
            ". ",            # Kalimat
            " ",             # Kata
            "",              # Karakter
        ]

        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=self.separators,
            length_function=len,
        )

    def chunk(self, text: str) -> list[str]:
        """
        Membagi teks menjadi chunks.

        Args:
            text: Teks yang akan di-chunk

        Returns:
            List of text chunks
        """
        # Bersihkan teks terlebih dahulu
        cleaned_text = self._clean_text(text)

        # Split menggunakan LangChain splitter
        chunks = self.splitter.split_text(cleaned_text)

        return chunks

    def chunk_with_metadata(self, text: str) -> list[dict]:
        """
        Membagi teks menjadi chunks dengan metadata.

        Args:
            text: Teks yang akan di-chunk

        Returns:
            List of dict dengan keys: text, metadata
        """
        chunks = self.chunk(text)
        result = []

        for idx, chunk in enumerate(chunks):
            metadata = self._extract_metadata(chunk, idx)
            result.append({
                "text": chunk,
                "metadata": metadata,
            })

        return result

    def _clean_text(self, text: str) -> str:
        """
        Membersihkan teks dari karakter yang tidak diperlukan.

        Args:
            text: Teks original

        Returns:
            Teks yang sudah dibersihkan
        """
        # Hapus multiple whitespace
        text = re.sub(r"\s+", " ", text)

        # Kembalikan newline untuk struktur dokumen
        text = re.sub(r" (BAB [IVXLCDM]+)", r"\n\n\1", text)
        text = re.sub(r" (Pasal \d+)", r"\n\n\1", text)
        text = re.sub(r" (Bagian [A-Za-z]+)", r"\n\n\1", text)
        text = re.sub(r" \((\d+)\) ", r"\n(\1) ", text)  # Ayat

        # Hapus header/footer yang berulang
        text = re.sub(r"- \d+ -", "", text)  # Nomor halaman

        return text.strip()

    def _extract_metadata(self, chunk: str, chunk_index: int) -> dict:
        """
        Extract metadata dari chunk (pasal, bab, ayat).

        Args:
            chunk: Text chunk
            chunk_index: Index chunk

        Returns:
            Dict metadata
        """
        metadata = {
            "chunk_index": chunk_index,
            "source": "UU No 27 Tahun 2022",
            "char_count": len(chunk),
        }

        # Extract BAB
        bab_match = re.search(r"BAB ([IVXLCDM]+)", chunk)
        if bab_match:
            metadata["bab"] = bab_match.group(1)

        # Extract Pasal
        pasal_match = re.search(r"Pasal (\d+)", chunk)
        if pasal_match:
            metadata["pasal"] = pasal_match.group(1)

        # Extract Ayat
        ayat_matches = re.findall(r"\((\d+)\)", chunk)
        if ayat_matches:
            metadata["ayat"] = ayat_matches

        return metadata


def chunk_uu_pdp(
    text: str,
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
) -> list[dict]:
    """
    Helper function untuk chunk teks UU PDP.

    Args:
        text: Teks UU PDP
        chunk_size: Ukuran chunk
        chunk_overlap: Overlap antar chunk

    Returns:
        List of chunks dengan metadata
    """
    chunker = TextChunker(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    return chunker.chunk_with_metadata(text)


if __name__ == "__main__":
    # Test chunking
    from pdf_loader import load_uu_pdp

    try:
        # Load PDF
        text = load_uu_pdp()
        print(f"✅ Loaded PDF: {len(text)} karakter")

        # Chunk text
        chunks = chunk_uu_pdp(text)
        print(f"✅ Created {len(chunks)} chunks")

        # Preview chunks
        print(f"\n--- Preview 3 chunks pertama ---\n")
        for i, chunk in enumerate(chunks[:3]):
            print(f"📄 Chunk {i + 1}:")
            print(f"   Metadata: {chunk['metadata']}")
            print(f"   Preview: {chunk['text'][:150]}...")
            print()

    except Exception as e:
        print(f"❌ Error: {e}")
