# Plan: DevOps Deployment - MCP PDP Server

## Deskripsi
Setup CI/CD pipeline menggunakan GitHub Actions untuk deploy MCP PDP Server ke development server lokal melalui Docker Registry dan SSH.

---

## Arsitektur Deployment

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   GitHub Repo   │────▶│  GitHub Actions  │────▶│  Docker Registry│
│   (Push/PR)     │     │  (Build & Push)  │     │  (GHCR/DockerHub)│
└─────────────────┘     └──────────────────┘     └─────────────────┘
                                                          │
                                                          ▼
                                                 ┌─────────────────┐
                                                 │   Dev Server    │
                                                 │   (SSH + Docker)│
                                                 └─────────────────┘
```

---

## Workflow Overview

### Trigger Events
| Event | Action |
|-------|--------|
| `push` ke `main` | Build → Push → Deploy ke Dev Server |
| `pull_request` ke `main` | Build → Test (tanpa deploy) |
| `workflow_dispatch` | Manual trigger deployment |

### Pipeline Steps

```
1. Checkout Code
       │
       ▼
2. Setup Python & Test
       │
       ▼
3. Build Docker Image
       │
       ▼
4. Push to Docker Registry (GHCR)
       │
       ▼
5. SSH to Dev Server
       │
       ▼
6. Pull & Run Docker Container
       │
       ▼
7. Health Check
```

---

## Tech Stack

| Komponen | Teknologi |
|----------|-----------|
| CI/CD | GitHub Actions |
| Container Registry | GitHub Container Registry (ghcr.io) |
| Container Runtime | Docker / Docker Compose |
| Deployment Method | SSH + Docker Pull |
| Server | Linux Dev Server (lokal) |

---

## File yang Akan Dibuat

```
latihan_mcp/
├── .github/
│   └── workflows/
│       ├── deploy.yml          # Main deployment workflow (UPDATE)
│       ├── pr-check.yml        # PR validation workflow (NEW)
│       └── docker-build.yml    # Reusable Docker build (NEW)
├── docker/
│   ├── Dockerfile              # Multi-stage Dockerfile
│   ├── docker-compose.yml      # Docker Compose untuk dev server
│   ├── docker-compose.prod.yml # Production override (optional)
│   └── .dockerignore           # Docker ignore file
├── scripts/
│   ├── deploy-docker.sh        # Deployment script untuk server
│   └── health-check.sh         # Health check script
└── deployment_devops.md        # Plan ini
```

---

## Tahapan Implementasi

### FASE 1: Docker Setup

#### 1.1 Dockerfile (Multi-stage Build)
```dockerfile
# Stage 1: Builder
FROM python:3.11-slim as builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY . .
ENV PATH=/root/.local/bin:$PATH
CMD ["python", "-m", "src.server"]
```

**Fitur:**
- Multi-stage untuk image size kecil
- Python 3.11 slim base
- Non-root user (optional security)

#### 1.2 Docker Compose
```yaml
version: '3.8'
services:
  mcp-pdp-server:
    image: ghcr.io/${GITHUB_REPOSITORY}:latest
    container_name: mcp-pdp-server
    restart: unless-stopped
    env_file:
      - .env
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
    healthcheck:
      test: ["CMD", "python", "-c", "print('OK')"]
      interval: 30s
      timeout: 10s
      retries: 3
```

#### 1.3 .dockerignore
```
venv/
__pycache__/
*.pyc
.git/
.env
*.md
.github/
```

---

### FASE 2: GitHub Actions Workflows

#### 2.1 Main Deploy Workflow (`.github/workflows/deploy.yml`)

**Trigger:** Push ke `main` branch

**Jobs:**
1. **test** - Run unit tests
2. **build** - Build & push Docker image ke GHCR
3. **deploy** - SSH ke dev server, pull & run container

```yaml
name: Deploy to Dev Server

on:
  push:
    branches: [main]
  workflow_dispatch:

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
      - run: pip install -r requirements.txt
      - run: python -m pytest tests/ (if exists)

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Login to GHCR
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - name: Build and Push
        uses: docker/build-push-action@v5
        with:
          push: true
          tags: ghcr.io/${{ github.repository }}:latest

  deploy:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - name: Deploy via SSH
        uses: appleboy/ssh-action@v1.0.3
        with:
          host: ${{ secrets.SSH_HOST }}
          username: ${{ secrets.SSH_USER }}
          key: ${{ secrets.SSH_PRIVATE_KEY }}
          script: |
            cd /opt/mcp-pdp-server
            docker compose pull
            docker compose up -d
            docker compose ps
```

#### 2.2 PR Check Workflow (`.github/workflows/pr-check.yml`)

**Trigger:** Pull Request ke `main`

**Jobs:**
1. **lint** - Code linting (ruff/black)
2. **test** - Run tests
3. **build-test** - Build Docker image (tanpa push)

```yaml
name: PR Check

on:
  pull_request:
    branches: [main]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pip install ruff black
      - run: ruff check .
      - run: black --check .

  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pip install -r requirements.txt
      - run: python -c "from src.server import mcp; print('OK')"

  build-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: docker/build-push-action@v5
        with:
          push: false
          tags: mcp-pdp-server:test
```

---

### FASE 3: Server Setup Scripts

#### 3.1 Deploy Script (`scripts/deploy-docker.sh`)
```bash
#!/bin/bash
# Script untuk deploy di dev server

set -e

PROJECT_DIR="/opt/mcp-pdp-server"
COMPOSE_FILE="docker/docker-compose.yml"

cd $PROJECT_DIR

# Pull latest image
docker compose -f $COMPOSE_FILE pull

# Stop old container
docker compose -f $COMPOSE_FILE down

# Start new container
docker compose -f $COMPOSE_FILE up -d

# Cleanup old images
docker image prune -f

# Show status
docker compose -f $COMPOSE_FILE ps
```

#### 3.2 Health Check Script (`scripts/health-check.sh`)
```bash
#!/bin/bash
# Health check untuk MCP server

MAX_RETRIES=5
RETRY_INTERVAL=5

for i in $(seq 1 $MAX_RETRIES); do
    if docker exec mcp-pdp-server python -c "print('healthy')"; then
        echo "✅ Server is healthy"
        exit 0
    fi
    echo "⏳ Waiting... ($i/$MAX_RETRIES)"
    sleep $RETRY_INTERVAL
done

echo "❌ Server health check failed"
exit 1
```

---

### FASE 4: GitHub Secrets Configuration

#### Required Secrets

| Secret Name | Description | Contoh |
|-------------|-------------|--------|
| `SSH_HOST` | IP/hostname dev server | `192.168.1.100` |
| `SSH_USER` | SSH username | `deploy` |
| `SSH_PRIVATE_KEY` | Private SSH key (full content) | `-----BEGIN OPENSSH...` |
| `SSH_PORT` | SSH port (optional, default 22) | `22` |

#### Environment Variables di Server

| Variable | Description |
|----------|-------------|
| `GOOGLE_API_KEY` | Google Gemini API key |
| `PINECONE_API_KEY` | Pinecone API key |
| `PINECONE_INDEX_NAME` | Nama index Pinecone |

---

### FASE 5: Dev Server Prerequisites

#### Server Requirements
```bash
# Install Docker
curl -fsSL https://get.docker.com | sh

# Install Docker Compose
sudo apt install docker-compose-plugin

# Add user to docker group
sudo usermod -aG docker $USER

# Create project directory
sudo mkdir -p /opt/mcp-pdp-server
sudo chown $USER:$USER /opt/mcp-pdp-server

# Create .env file
cat > /opt/mcp-pdp-server/.env << EOF
GOOGLE_API_KEY=your_google_api_key
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_INDEX_NAME=uu-pdp-27-2022
EOF
```

#### SSH Key Setup
```bash
# Di local machine, generate key
ssh-keygen -t ed25519 -C "github-actions-deploy"

# Copy public key ke server
ssh-copy-id -i ~/.ssh/id_ed25519.pub user@dev-server

# Copy private key content ke GitHub Secret
cat ~/.ssh/id_ed25519
```

---

## Workflow Diagram

### Push to Main (Auto Deploy)
```
Developer Push
      │
      ▼
┌─────────────────┐
│ GitHub Actions  │
│ ┌─────────────┐ │
│ │    Test     │ │
│ └──────┬──────┘ │
│        ▼        │
│ ┌─────────────┐ │
│ │ Build Image │ │
│ └──────┬──────┘ │
│        ▼        │
│ ┌─────────────┐ │
│ │ Push to GHCR│ │
│ └──────┬──────┘ │
│        ▼        │
│ ┌─────────────┐ │
│ │ SSH Deploy  │ │
│ └─────────────┘ │
└─────────────────┘
      │
      ▼
┌─────────────────┐
│   Dev Server    │
│ docker pull     │
│ docker up -d    │
└─────────────────┘
```

### Pull Request (Validation Only)
```
Developer PR
      │
      ▼
┌─────────────────┐
│ GitHub Actions  │
│ ┌─────────────┐ │
│ │    Lint     │ │
│ └──────┬──────┘ │
│        ▼        │
│ ┌─────────────┐ │
│ │    Test     │ │
│ └──────┬──────┘ │
│        ▼        │
│ ┌─────────────┐ │
│ │ Build Test  │ │
│ │ (no push)   │ │
│ └─────────────┘ │
└─────────────────┘
      │
      ▼
   ✅ / ❌
   PR Status
```

---

## Checklist Implementasi

### File yang Dibuat
- [ ] `docker/Dockerfile`
- [ ] `docker/docker-compose.yml`
- [ ] `docker/.dockerignore`
- [ ] `.github/workflows/deploy.yml` (update)
- [ ] `.github/workflows/pr-check.yml` (new)
- [ ] `scripts/deploy-docker.sh`
- [ ] `scripts/health-check.sh`

### GitHub Setup
- [ ] Enable GitHub Container Registry (GHCR)
- [ ] Set repository secrets (SSH_HOST, SSH_USER, SSH_PRIVATE_KEY)
- [ ] Enable Actions permissions

### Server Setup
- [ ] Install Docker & Docker Compose
- [ ] Setup SSH key authentication
- [ ] Create project directory
- [ ] Create .env file dengan credentials
- [ ] Test docker pull dari GHCR

---

## Timeline Estimasi

| Fase | Task | Durasi |
|------|------|--------|
| 1 | Docker Setup (Dockerfile, Compose) | 30 menit |
| 2 | GitHub Actions Workflows | 45 menit |
| 3 | Server Scripts | 15 menit |
| 4 | GitHub Secrets Configuration | 15 menit |
| 5 | Server Prerequisites | 30 menit |
| 6 | Testing & Debugging | 45 menit |
| **Total** | | **~3 jam** |

---

## Informasi yang Dibutuhkan dari Anda

Sebelum implementasi, saya butuh informasi berikut:

1. **SSH Server Details:**
   - IP/Hostname dev server: `___________`
   - SSH Username: `___________`
   - SSH Port (default 22): `___________`

2. **Docker Registry Preference:**
   - [ ] GitHub Container Registry (ghcr.io) - **Recommended**
   - [ ] Docker Hub
   - [ ] Self-hosted registry

3. **Project Directory di Server:**
   - Path: `/opt/mcp-pdp-server` (atau custom: `___________`)

---

## Approval Required

Silakan review plan ini. Setelah disetujui dan informasi di atas dilengkapi, saya akan mulai implementasi.

**Konfirmasi untuk memulai implementasi?** ✅
