"""
PDF Loader Module
=================

Module untuk extract teks dari dokumen PDF UU PDP.
"""

import os
from pathlib import Path
from typing import Optional

import fitz  # PyMuPDF


class PDFLoader:
    """Load dan extract teks dari file PDF."""

    def __init__(self, file_path: str | Path):
        """
        Initialize PDF Loader.

        Args:
            file_path: Path ke file PDF
        """
        self.file_path = Path(file_path)
        if not self.file_path.exists():
            raise FileNotFoundError(f"File tidak ditemukan: {self.file_path}")
        if not self.file_path.suffix.lower() == ".pdf":
            raise ValueError(f"File harus berformat PDF: {self.file_path}")

    def load(self) -> str:
        """
        Load dan extract semua teks dari PDF.

        Returns:
            String berisi seluruh teks dari PDF
        """
        text_content = []

        with fitz.open(self.file_path) as doc:
            for page_num, page in enumerate(doc, start=1):
                page_text = page.get_text("text")
                if page_text.strip():
                    text_content.append(page_text)

        return "\n\n".join(text_content)

    def load_pages(self) -> list[dict]:
        """
        Load PDF dan return teks per halaman.

        Returns:
            List of dict dengan keys: page_number, text
        """
        pages = []

        with fitz.open(self.file_path) as doc:
            for page_num, page in enumerate(doc, start=1):
                page_text = page.get_text("text")
                if page_text.strip():
                    pages.append({
                        "page_number": page_num,
                        "text": page_text.strip(),
                    })

        return pages

    def get_metadata(self) -> dict:
        """
        Get metadata dari PDF.

        Returns:
            Dict berisi metadata PDF
        """
        with fitz.open(self.file_path) as doc:
            metadata = doc.metadata
            metadata["page_count"] = doc.page_count
            return metadata


def load_uu_pdp(data_dir: Optional[str] = None) -> str:
    """
    Helper function untuk load UU PDP dari folder data.

    Args:
        data_dir: Path ke folder data (optional)

    Returns:
        Teks lengkap UU PDP
    """
    if data_dir is None:
        # Default: folder data di root project
        current_dir = Path(__file__).parent.parent.parent
        data_dir = current_dir / "data"

    pdf_path = Path(data_dir) / "UU Nomor 27 Tahun 2022.pdf"

    if not pdf_path.exists():
        raise FileNotFoundError(
            f"File UU PDP tidak ditemukan di: {pdf_path}\n"
            "Pastikan file 'UU Nomor 27 Tahun 2022.pdf' ada di folder 'data/'"
        )

    loader = PDFLoader(pdf_path)
    return loader.load()


if __name__ == "__main__":
    # Test loading PDF
    try:
        text = load_uu_pdp()
        print(f"✅ Berhasil load PDF")
        print(f"📄 Total karakter: {len(text)}")
        print(f"\n--- Preview (500 karakter pertama) ---\n")
        print(text[:500])
    except Exception as e:
        print(f"❌ Error: {e}")
