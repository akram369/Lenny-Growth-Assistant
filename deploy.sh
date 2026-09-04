#!/usr/bin/env bash
# ==============================================================================
# The Lenny Growth Assistant - Automated Production Deployment Script
# Target: Ubuntu 22.04 / 24.04 LTS or Debian Linux Server
# ==============================================================================

set -euo pipefail

# Visual formatting
BOLD='\033[1m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BOLD}${BLUE}================================================================${NC}"
echo -e "${BOLD}${BLUE}   🚀 Deploying The Lenny Growth Assistant (Production)        ${NC}"
echo -e "${BOLD}${BLUE}================================================================${NC}\n"

# 1. Check & Install Docker if not present
if ! command -v docker &> /dev/null; then
    echo -e "${YELLOW}⚙️  Docker not detected. Installing Docker Engine and Compose plugin...${NC}"
    sudo apt-get update -y
    sudo apt-get install -y ca-certificates curl gnupg lsb-release git

    sudo install -m 0755 -d /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    sudo chmod a+r /etc/apt/keyrings/docker.gpg

    echo \
      "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
      $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

    sudo apt-get update -y
    sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
    sudo systemctl enable --now docker
    echo -e "${GREEN}✅ Docker installed successfully.${NC}\n"
else
    echo -e "${GREEN}✅ Docker is already installed: $(docker --version)${NC}\n"
fi

# 2. Setup Environment Variables
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚙️  Creating .env from .env.example...${NC}"
    cp .env.example .env
    echo -e "${GREEN}✅ Default .env configured.${NC}\n"
else
    echo -e "${GREEN}✅ Existing .env found.${NC}\n"
fi

# 3. Build & Launch Docker Compose Stack
echo -e "${BLUE}📦 Building and launching containers (Postgres pgvector, Ollama, Backend, Frontend)...${NC}"
docker compose down --remove-orphans || true
docker compose up -d --build

echo -e "${YELLOW}⏳ Waiting for services to initialize...${NC}"
sleep 8

# 4. Pull Local Model into Ollama
echo -e "\n${BLUE}🦙 Pulling llama3.2:3b model into Ollama container...${NC}"
docker compose exec ollama ollama pull llama3.2:3b
echo -e "${GREEN}✅ Local LLM weights ready.${NC}\n"

# 5. Ingest Sample Transcripts & Build pgvector HNSW Index
echo -e "${BLUE}📚 Ingesting podcast transcripts & computing embeddings...${NC}"
docker compose exec backend python scripts/ingest.py --clear
echo -e "${GREEN}✅ Vector index initialized.${NC}\n"

# 6. Verify System Health Probe
echo -e "${BLUE}🩺 Running health diagnostics probe...${NC}"
HEALTH_JSON=$(docker compose exec backend curl -s http://localhost:8001/api/health || echo "{}")

echo -e "${GREEN}Probe Output:${NC}"
echo "$HEALTH_JSON"

# Detect Public Server IP
SERVER_IP=$(curl -s -4 ifconfig.me || hostname -I | awk '{print $1}')

echo -e "\n${BOLD}${GREEN}================================================================${NC}"
echo -e "${BOLD}${GREEN}   🎉 The Lenny Growth Assistant is LIVE & OPERATIONAL!        ${NC}"
echo -e "${BOLD}${GREEN}================================================================${NC}"
echo -e "   🖥️  ${BOLD}Web Frontend UI:${NC}    http://${SERVER_IP}:3000"
echo -e "   🔌  ${BOLD}FastAPI Backend API:${NC} http://${SERVER_IP}:8001"
echo -e "   📖  ${BOLD}Swagger API Docs:${NC}    http://${SERVER_IP}:8001/docs"
echo -e "   🩺  ${BOLD}Health Diagnostics:${NC} http://${SERVER_IP}:8001/api/health"
echo -e "${BOLD}${GREEN}================================================================${NC}\n"
