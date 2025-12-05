# MCP PDP Server - UU No 27 Tahun 2022

Server MCP (Model Context Protocol) untuk menjawab pertanyaan terkait UU Perlindungan Data Pribadi menggunakan RAG dengan Pinecone dan Google Gemini.

## 🚀 Quick Start (Local)

```bash
# 1. Setup virtual environment
python3.11 -m venv venv
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Setup environment variables
cp .env.example .env
# Edit .env dengan API keys Anda

# 4. Run server
python -m src.server
```

## 🐳 Docker

### Build & Run Locally
```bash
docker build -t mcp-pdp-server .
docker run -d --name mcp-pdp-server \
  -p 8000:8000 \
  -e GOOGLE_API_KEY=your_key \
  -e PINECONE_API_KEY=your_key \
  -e PINECONE_INDEX_NAME=uu-pdp-27-2022 \
  mcp-pdp-server
```

### Docker Compose
```bash
# Edit .env file terlebih dahulu
docker-compose up -d
```

## 🔧 GitHub Actions Deployment

### Setup GitHub Secrets

Buka repository GitHub → Settings → Secrets and variables → Actions → New repository secret

Tambahkan secrets berikut:

| Secret Name | Value | Keterangan |
|------------|-------|------------|
| `SSH_HOST` | `103.164.191.212` | IP server |
| `SSH_PORT` | `22193` | SSH port |
| `SSH_USER` | `devjc` | SSH username |
| `SSH_PRIVATE_KEY` | (isi file devops01_openssh.pem) | SSH private key (OpenSSH format) |
| `DEPLOY_PATH` | `/home/devjc/mcp-pdp-server` | Path di server |
| `GHCR_TOKEN` | (GitHub PAT) | Token untuk pull image |
| `GOOGLE_API_KEY` | `AIzaSyBKJy...` | Google API key |
| `PINECONE_API_KEY` | `pcsk_6Rn8S4...` | Pinecone API key |
| `PINECONE_INDEX_NAME` | `uu-pdp-27-2022` | Nama index Pinecone |

### Cara mendapatkan SSH_PRIVATE_KEY

```bash
cat devops01_openssh.pem
# Copy seluruh isi file termasuk -----BEGIN RSA PRIVATE KEY----- dan -----END RSA PRIVATE KEY-----
```

### Cara mendapatkan GHCR_TOKEN

1. Buka https://github.com/settings/tokens
2. Generate new token (classic)
3. Beri nama: `GHCR Deploy Token`
4. Pilih scope: `read:packages`, `write:packages`
5. Copy token dan simpan sebagai secret `GHCR_TOKEN`

## 📦 CI/CD Pipeline

```
Push ke main/master
       │
       ▼
   ┌─────────┐
   │  Test   │ ← Syntax check Python
   └────┬────┘
        │
        ▼
   ┌─────────┐
   │  Build  │ ← Build Docker image
   └────┬────┘
        │
        ▼
   ┌─────────┐
   │  Push   │ ← Push ke ghcr.io
   └────┬────┘
        │
        ▼
   ┌─────────┐
   │ Deploy  │ ← SSH ke server, pull & run
   └─────────┘
```

## 🛠️ Manual Deployment

SSH ke server dan jalankan:

```bash
# Download deploy script
curl -O https://raw.githubusercontent.com/mulyana08/latihan_mcp/main/scripts/deploy.sh
chmod +x deploy.sh

# Setup .env
cat > .env << EOF
GOOGLE_API_KEY=your_key
PINECONE_API_KEY=your_key
PINECONE_INDEX_NAME=uu-pdp-27-2022
EOF

# Deploy
./deploy.sh
```

## 📋 MCP Tools

Server ini menyediakan tools berikut:

| Tool | Deskripsi |
|------|-----------|
| `tanya_pdp` | Tanya jawab tentang UU PDP menggunakan RAG |
| `cari_pasal` | Cari pasal tertentu dalam UU PDP |
| `ringkasan_bab` | Dapatkan ringkasan per bab |
| `info_uu_pdp` | Informasi umum tentang UU PDP |

## 📁 Project Structure

```
latihan_mcp/
├── src/
│   ├── server.py          # MCP Server
│   ├── pdp_tools.py        # Tool definitions
│   ├── document/
│   │   ├── pdf_loader.py   # PDF extractor
│   │   └── chunker.py      # Text chunker
│   └── rag/
│       ├── embeddings.py   # Google embeddings
│       ├── pinecone_client.py # Vector DB
│       └── retriever.py    # RAG retriever
├── data/
│   └── uu_pdp_27_2022.pdf  # Dokumen UU PDP
├── scripts/
│   └── deploy.sh           # Deploy script
├── .github/
│   └── workflows/
│       └── deploy.yml      # GitHub Actions
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## 📝 License

MIT
