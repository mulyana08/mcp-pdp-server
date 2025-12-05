#!/bin/bash
#
# Deploy Script untuk MCP PDP Server
# ===================================
#
# Usage:
#   ./deploy.sh [command]
#
# Commands:
#   install   - Install dependencies dan setup
#   start     - Start server
#   stop      - Stop server
#   restart   - Restart server
#   status    - Check status
#   logs      - View logs
#   ingest    - Run document ingestion
#

set -e

# Configuration
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$PROJECT_DIR/venv"
PID_FILE="$PROJECT_DIR/server.pid"
LOG_FILE="$PROJECT_DIR/server.log"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if venv exists
check_venv() {
    if [ ! -d "$VENV_DIR" ]; then
        log_error "Virtual environment not found. Run './deploy.sh install' first."
        exit 1
    fi
}

# Install command
cmd_install() {
    log_info "Installing MCP PDP Server..."

    # Create venv if not exists
    if [ ! -d "$VENV_DIR" ]; then
        log_info "Creating virtual environment..."
        python3 -m venv "$VENV_DIR"
    fi

    # Activate and install
    source "$VENV_DIR/bin/activate"
    log_info "Installing dependencies..."
    pip install --upgrade pip
    pip install -r "$PROJECT_DIR/requirements.txt"

    # Create .env if not exists
    if [ ! -f "$PROJECT_DIR/.env" ]; then
        if [ -f "$PROJECT_DIR/.env.example" ]; then
            cp "$PROJECT_DIR/.env.example" "$PROJECT_DIR/.env"
            log_warn ".env created from example. Please update with actual credentials."
        fi
    fi

    log_info "Installation complete!"
    echo ""
    echo "Next steps:"
    echo "  1. Edit .env with your API keys"
    echo "  2. Run './deploy.sh ingest' to index documents"
    echo "  3. Run './deploy.sh start' to start the server"
}

# Start command
cmd_start() {
    check_venv

    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p $PID > /dev/null 2>&1; then
            log_warn "Server already running (PID: $PID)"
            return
        fi
    fi

    log_info "Starting MCP PDP Server..."
    source "$VENV_DIR/bin/activate"

    cd "$PROJECT_DIR"
    nohup python -m src.server > "$LOG_FILE" 2>&1 &
    echo $! > "$PID_FILE"

    sleep 2

    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p $PID > /dev/null 2>&1; then
            log_info "Server started successfully (PID: $PID)"
        else
            log_error "Server failed to start. Check logs: $LOG_FILE"
            exit 1
        fi
    fi
}

# Stop command
cmd_stop() {
    if [ ! -f "$PID_FILE" ]; then
        log_warn "PID file not found. Server may not be running."
        return
    fi

    PID=$(cat "$PID_FILE")

    if ps -p $PID > /dev/null 2>&1; then
        log_info "Stopping server (PID: $PID)..."
        kill $PID
        sleep 2

        if ps -p $PID > /dev/null 2>&1; then
            log_warn "Server still running. Force killing..."
            kill -9 $PID
        fi

        rm -f "$PID_FILE"
        log_info "Server stopped."
    else
        log_warn "Server not running (stale PID file)."
        rm -f "$PID_FILE"
    fi
}

# Restart command
cmd_restart() {
    cmd_stop
    sleep 1
    cmd_start
}

# Status command
cmd_status() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p $PID > /dev/null 2>&1; then
            log_info "Server is running (PID: $PID)"
            echo ""
            echo "Process info:"
            ps -p $PID -o pid,ppid,user,%cpu,%mem,etime,command
        else
            log_warn "Server not running (stale PID file)"
        fi
    else
        log_warn "Server not running (no PID file)"
    fi
}

# Logs command
cmd_logs() {
    if [ -f "$LOG_FILE" ]; then
        tail -f "$LOG_FILE"
    else
        log_warn "Log file not found: $LOG_FILE"
    fi
}

# Ingest command
cmd_ingest() {
    check_venv
    log_info "Running document ingestion..."

    source "$VENV_DIR/bin/activate"
    cd "$PROJECT_DIR"
    python scripts/ingest_documents.py
}

# Help command
cmd_help() {
    echo "MCP PDP Server Deploy Script"
    echo ""
    echo "Usage: ./deploy.sh [command]"
    echo ""
    echo "Commands:"
    echo "  install   Install dependencies and setup"
    echo "  start     Start the server"
    echo "  stop      Stop the server"
    echo "  restart   Restart the server"
    echo "  status    Check server status"
    echo "  logs      View server logs (tail -f)"
    echo "  ingest    Run document ingestion to Pinecone"
    echo "  help      Show this help message"
}

# Main
case "${1:-help}" in
    install)
        cmd_install
        ;;
    start)
        cmd_start
        ;;
    stop)
        cmd_stop
        ;;
    restart)
        cmd_restart
        ;;
    status)
        cmd_status
        ;;
    logs)
        cmd_logs
        ;;
    ingest)
        cmd_ingest
        ;;
    help|--help|-h)
        cmd_help
        ;;
    *)
        log_error "Unknown command: $1"
        cmd_help
        exit 1
        ;;
esac
