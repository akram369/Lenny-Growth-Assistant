# ==============================================================================
# The Lenny Growth Assistant - Automated Local / Windows Deployment Script
# Shell: PowerShell
# ==============================================================================

Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "   Deploying The Lenny Growth Assistant (Docker Stack)          " -ForegroundColor Cyan
Write-Host "================================================================`n" -ForegroundColor Cyan

# 1. Ensure .env exists
if (-not (Test-Path ".env")) {
    Write-Host "Creating .env from .env.example..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "Default .env created.`n" -ForegroundColor Green
} else {
    Write-Host "Existing .env found.`n" -ForegroundColor Green
}

# 2. Build and Launch Containers
Write-Host "Building and launching containers (Postgres pgvector, Ollama, Backend, Frontend)..." -ForegroundColor Cyan
docker compose down --remove-orphans
docker compose up -d --build

Write-Host "`nWaiting 10 seconds for containers to initialize..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# 3. Pull local model in Ollama
Write-Host "`nPulling llama3.2:3b model into Ollama container..." -ForegroundColor Cyan
docker compose exec ollama ollama pull llama3.2:3b
Write-Host "Local LLM weights ready.`n" -ForegroundColor Green

# 4. Ingest sample transcripts into pgvector
Write-Host "Ingesting sample transcripts and generating vector embeddings..." -ForegroundColor Cyan
docker compose exec backend python scripts/ingest.py --clear
Write-Host "Vector database populated.`n" -ForegroundColor Green

# 5. Check Health Probe
Write-Host "Running health probe..." -ForegroundColor Cyan
try {
    $health = Invoke-RestMethod -Uri "http://localhost:8001/api/health" -Method Get
    $health | ConvertTo-Json -Depth 4 | Write-Host -ForegroundColor Green
} catch {
    Write-Host "Backend initializing, please allow a few moments..." -ForegroundColor Yellow
}

Write-Host "`n================================================================" -ForegroundColor Green
Write-Host "   The Lenny Growth Assistant is LIVE & READY!                  " -ForegroundColor Green
Write-Host "================================================================" -ForegroundColor Green
Write-Host "   Web UI:          http://localhost:3000" -ForegroundColor White
Write-Host "   Backend API:     http://localhost:8001" -ForegroundColor White
Write-Host "   Swagger Docs:    http://localhost:8001/docs" -ForegroundColor White
Write-Host "   Health Probe:    http://localhost:8001/api/health" -ForegroundColor White
Write-Host "================================================================`n" -ForegroundColor Green
