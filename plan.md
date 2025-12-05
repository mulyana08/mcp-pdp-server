# Plan: MCP Server untuk PDP (Proteksi Data Pribadi)

## Deskripsi Proyek
Server MCP menggunakan FastMCP untuk menjawab pertanyaan seputar Perlindungan Data Pribadi (PDP) berdasarkan **UU Nomor 27 Tahun 2022 tentang Perlindungan Data Pribadi**. Menggunakan teknologi RAG (Retrieval-Augmented Generation) dengan Pinecone sebagai vector database.

---

## Arsitektur Sistem

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   MCP Client    │────▶│   FastMCP Server │────▶│    Pinecone     │
│   (Claude, etc) │     │   (Python)       │     │  Vector DB      │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                               │
                               ▼
                        ┌──────────────────┐
                        │   Google AI      │
                        │   (Embeddings +  │
                        │   Gemini Flash)  │
                        └──────────────────┘
```

---

## Tech Stack

| Komponen | Teknologi |
|----------|-----------|
| MCP Framework | FastMCP (Python) |
| Vector Database | Pinecone (Free Tier) |
| Embeddings | Google `text-embedding-004` |
| LLM | Google `gemini-2.0-flash` |
| PDF Processing | PyMuPDF / pdfplumber |
| Text Splitting | LangChain Text Splitters |
| Deployment | SSH Server via GitHub Actions |

---

## Struktur Folder

```
latihan_mcp/
├── src/                       # Source code utama
│   ├── __init__.py
│   ├── server.py              # FastMCP server utama
│   ├── rag/                   # RAG components
│   │   ├── __init__.py
│   │   ├── embeddings.py      # Google embeddings handler
│   │   ├── pinecone_client.py # Pinecone operations
│   │   └── retriever.py       # RAG retrieval logic
│   ├── document/              # Document processing
│   │   ├── __init__.py
│   │   ├── pdf_loader.py      # PDF extraction
│   │   └── chunker.py         # Text chunking
│   └── tools/                 # MCP Tools
│       ├── __init__.py
│       └── pdp_tools.py       # MCP tools untuk PDP
├── scripts/                   # Utility scripts
│   ├── ingest_documents.py    # Script untuk indexing PDF ke Pinecone
│   └── test_rag.py            # Testing RAG locally
├── data/                      # Data files
│   └── UU Nomor 27 Tahun 2022.pdf
├── .github/                   # GitHub Actions
│   └── workflows/
│       └── deploy.yml         # Deployment workflow
├── requirements.txt           # Python dependencies
├── pyproject.toml             # Project configuration
├── .env.example               # Environment template
├── .env                       # Environment variables (gitignored)
├── .gitignore                 # Git ignore rules
├── Dockerfile                 # Optional: containerized deployment
├── deploy.sh                  # Deployment script
└── README.md                  # Project documentation
```

---

## Tahapan Implementasi

### ✅ FASE 1: Setup Struktur Project (SELESAI)

#### 1.1 Buat Struktur Folder
```
latihan_mcp/
├── src/
│   ├── __init__.py
│   ├── server.py
│   ├── rag/
│   │   ├── __init__.py
│   │   ├── embeddings.py
│   │   ├── pinecone_client.py
│   │   └── retriever.py
│   ├── document/
│   │   ├── __init__.py
│   │   ├── pdf_loader.py
│   │   └── chunker.py
│   └── tools/
│       ├── __init__.py
│       └── pdp_tools.py
├── scripts/
│   ├── ingest_documents.py
│   └── test_rag.py
├── data/
│   └── UU Nomor 27 Tahun 2022.pdf
├── .github/
│   └── workflows/
│       └── deploy.yml
├── requirements.txt
├── pyproject.toml
├── .env.example
├── .env
├── .gitignore
├── deploy.sh
└── README.md
```

#### 1.2 File yang Akan Dibuat (Fase 1)

| No | File | Deskripsi |
|----|------|-----------|
| 1 | `requirements.txt` | Dependencies Python |
| 2 | `pyproject.toml` | Konfigurasi project |
| 3 | `.env.example` | Template environment variables |
| 4 | `.gitignore` | Ignore files untuk Git |
| 5 | `src/__init__.py` | Package init |
| 6 | `src/rag/__init__.py` | RAG package init |
| 7 | `src/document/__init__.py` | Document package init |
| 8 | `src/tools/__init__.py` | Tools package init |
| 9 | `README.md` | Dokumentasi project |

---

### ✅ FASE 2: Document Processing (SELESAI)
- `src/document/pdf_loader.py` ✅
- `src/document/chunker.py` ✅

### ✅ FASE 3: RAG & Embeddings (SELESAI)
- `src/rag/embeddings.py` ✅
- `src/rag/pinecone_client.py` ✅
- `src/rag/retriever.py` ✅
- `scripts/ingest_documents.py` ✅

### ✅ FASE 4: MCP Server & Tools (SELESAI)
- `src/tools/pdp_tools.py` ✅
- `src/server.py` ✅

### ✅ FASE 5: Deployment & CI/CD (SELESAI)
- `.github/workflows/deploy.yml` ✅
- `deploy.sh` ✅
- `scripts/test_rag.py` ✅
- `scripts/test_rag.py`

---

### Tahap 1: Setup Project & Dependencies
**File: `requirements.txt`**
- fastmcp
- pinecone-client
- google-generativeai
- pymupdf (fitz)
- langchain-text-splitters
- python-dotenv
- uvicorn

**File: `pyproject.toml`**
- Konfigurasi project Python

**File: `.env.example`**
- Template environment variables

---

### Tahap 2: PDF Document Processing
**File: `src/document/pdf_loader.py`**
- Fungsi untuk extract teks dari PDF UU No 27
- Membersihkan formatting dan whitespace

**File: `src/document/chunker.py`**
- Membagi dokumen menjadi chunks yang sesuai
- Menggunakan RecursiveCharacterTextSplitter
- Chunk size: 1000 characters, overlap: 200

---

### Tahap 3: Embeddings & Vector Store
**File: `src/rag/embeddings.py`**
- Wrapper untuk Google Generative AI embeddings API
- Model: `text-embedding-004` (dimensi: 768)

**File: `src/rag/pinecone_client.py`**
- Initialize Pinecone client
- Create/connect to index
- Upsert dan query vectors

**File: `scripts/ingest_documents.py`**
- Script one-time untuk:
  1. Load PDF
  2. Chunk dokumen
  3. Generate embeddings
  4. Upload ke Pinecone

---

### Tahap 4: RAG Retriever
**File: `src/rag/retriever.py`**
- Query Pinecone dengan user question
- Retrieve top-k relevant chunks
- Format context untuk LLM prompt

---

### Tahap 5: MCP Tools Definition
**File: `src/tools/pdp_tools.py`**
- Tool: `tanya_pdp` - Menjawab pertanyaan tentang UU PDP
- Tool: `cari_pasal` - Mencari pasal spesifik
- Tool: `ringkasan_bab` - Memberikan ringkasan per bab

---

### Tahap 6: FastMCP Server
**File: `src/server.py`**
- Main FastMCP server
- Register tools
- Handle requests dengan RAG

---

### Tahap 7: GitHub Actions Deployment
**File: `.github/workflows/deploy.yml`**
- Trigger: push to main branch
- Steps:
  1. Checkout code
  2. Setup SSH key
  3. Deploy ke development server via SSH
  4. Restart service

**File: `deploy.sh`**
- Script deployment di server:
  1. Pull latest code
  2. Install dependencies
  3. Restart MCP server (systemd/supervisor)

---

## Detail Implementasi

### 1. FastMCP Server (`src/server.py`)

```python
# Pseudo-code structure
from fastmcp import FastMCP
from tools.pdp_tools import tanya_pdp, cari_pasal, ringkasan_bab

mcp = FastMCP("PDP-Assistant")

@mcp.tool()
async def tanya_pdp(pertanyaan: str) -> str:
    """Menjawab pertanyaan seputar UU Perlindungan Data Pribadi No 27 Tahun 2022"""
    # 1. Generate embedding dari pertanyaan
    # 2. Query Pinecone untuk context
    # 3. Generate response dengan LLM
    pass

@mcp.tool()
async def cari_pasal(nomor_pasal: int) -> str:
    """Mencari isi pasal tertentu dalam UU PDP"""
    pass

@mcp.tool()
async def ringkasan_bab(nomor_bab: int) -> str:
    """Memberikan ringkasan dari bab tertentu dalam UU PDP"""
    pass
```

### 2. Pinecone Setup

```python
# Pseudo-code for Pinecone
import pinecone

# Index configuration
INDEX_NAME = "uu-pdp-27-2022"
DIMENSION = 768  # Google embedding dimension
METRIC = "cosine"

# Metadata structure per vector
{
    "text": "chunk content",
    "pasal": "1",
    "bab": "I",
    "ayat": "2",
    "source": "UU No 27 Tahun 2022"
}
```

### 3. RAG Flow

```
User Question
     │
     ▼
Generate Embedding (Google Gemini)
     │
     ▼
Query Pinecone (top_k=5)
     │
     ▼
Retrieve Relevant Chunks
     │
     ▼
Construct Prompt with Context
     │
     ▼
Generate Response (Gemini Flash)
     │
     ▼
Return Answer to User
```

---

## GitHub Actions Workflow

### File: `.github/workflows/deploy.yml`

```yaml
name: Deploy MCP Server

on:
  push:
    branches: [main]
  workflow_dispatch:

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Setup SSH Key
        uses: webfactory/ssh-agent@v0.8.0
        with:
          ssh-private-key: ${{ secrets.SSH_PRIVATE_KEY }}

      - name: Add SSH Known Hosts
        run: |
          mkdir -p ~/.ssh
          ssh-keyscan -H ${{ secrets.SSH_HOST }} >> ~/.ssh/known_hosts

      - name: Deploy to Development Server
        run: |
          ssh ${{ secrets.SSH_USER }}@${{ secrets.SSH_HOST }} << 'EOF'
            cd /path/to/mcp-pdp-server
            git pull origin main
            source venv/bin/activate
            pip install -r requirements.txt
            sudo systemctl restart mcp-pdp-server
          EOF

      - name: Verify Deployment
        run: |
          ssh ${{ secrets.SSH_USER }}@${{ secrets.SSH_HOST }} \
            "systemctl status mcp-pdp-server --no-pager"
```

### Required GitHub Secrets

| Secret Name | Description |
|-------------|-------------|
| `SSH_PRIVATE_KEY` | Private SSH key untuk akses server |
| `SSH_HOST` | IP/hostname development server |
| `SSH_USER` | Username SSH |
| `GOOGLE_API_KEY` | Google AI API key (Gemini) |
| `PINECONE_API_KEY` | Pinecone API key |

---

## Environment Variables

### File: `.env.example`

```env
# Google AI (Gemini)
GOOGLE_API_KEY=AIzaSyBKJy2QcsJtjiq3poCQuc3kHeXSjnSrZBs

# Pinecone
PINECONE_API_KEY=pcsk_6Rn8S4_AW6depUSQgzLB59QhY88Vzp79uYec2xhcgZgvCz6o2YmRLmUiGQM5KCE7sXYxbC
PINECONE_ENVIRONMENT=gcp-starter
PINECONE_INDEX_NAME=uu-pdp-27-2022

# Server
MCP_HOST=0.0.0.0
MCP_PORT=8000
```

---

## Server Setup (SSH Development Server)

### Systemd Service

**File: `/etc/systemd/system/mcp-pdp-server.service`**

```ini
[Unit]
Description=MCP PDP Server
After=network.target

[Service]
Type=simple
User=deploy
WorkingDirectory=/path/to/mcp-pdp-server
Environment="PATH=/path/to/mcp-pdp-server/venv/bin"
EnvironmentFile=/path/to/mcp-pdp-server/.env
ExecStart=/path/to/mcp-pdp-server/venv/bin/python -m src.server
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

---

## Testing Plan

### Local Testing
1. Run `scripts/test_rag.py` untuk test retrieval
2. Test setiap tool secara individual
3. Test full MCP server dengan MCP inspector

### Integration Testing
1. Connect dengan Claude Desktop
2. Test berbagai jenis pertanyaan PDP
3. Validasi akurasi jawaban dengan UU asli

---

## Timeline Estimasi

| Tahap | Durasi |
|-------|--------|
| Setup Project & Dependencies | 30 menit |
| PDF Processing | 1 jam |
| Embeddings & Pinecone Setup | 1 jam |
| RAG Retriever | 1 jam |
| MCP Tools | 1-2 jam |
| FastMCP Server | 1 jam |
| GitHub Actions | 30 menit |
| Testing & Debugging | 2 jam |
| **Total** | **~8-9 jam** |

---

## Checklist Sebelum Deployment

- [ ] Pinecone index sudah dibuat dan terisi
- [ ] Environment variables sudah di-set di server
- [ ] SSH key sudah dikonfigurasi di GitHub Secrets
- [ ] Systemd service sudah dibuat di server
- [ ] Firewall port sudah dibuka (jika perlu)
- [ ] Test local berhasil
- [ ] README.md sudah lengkap

---

## Catatan Penting

1. **Biaya**: 
   - Pinecone Free Tier: 1 index, 100K vectors
   - Google Gemini Flash: **GRATIS** (dengan rate limit generous)
   - Google Embedding: **GRATIS** hingga 1500 requests/menit

2. **Keamanan**:
   - Jangan commit `.env` file
   - Gunakan secrets untuk credentials
   - Validasi input dari user

3. **Maintenance**:
   - Monitor Pinecone usage
   - Log semua queries untuk improvement
   - Update embedding jika UU direvisi

---

## Approval Required

Silakan review plan ini. Setelah disetujui, saya akan mulai implementasi kode sesuai tahapan di atas.

**Konfirmasi untuk memulai coding?** ✅
