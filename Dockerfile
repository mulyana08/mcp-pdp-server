# MCP PDP Server - UU No 27 Tahun 2022
# Using Microsoft Container Registry (more stable than Docker Hub)

FROM mcr.microsoft.com/devcontainers/python:3.11-bookworm

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY data/ ./data/

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "print('healthy')" || exit 1

# Expose port for MCP server
EXPOSE 8000

# Start MCP server
CMD ["python", "-m", "src.server"]
