# Logs Directory

This directory contains service logs and status files.

## Status Files (updated every 30s by services)

- `backend_status.json` - Backend API health
- `rag_status.json` - RAG service status
- `latex_status.json` - LaTeX watcher status

## Log Files

- `backend.log` - Backend application logs
- `rag.log` - RAG indexing/search logs
- `latex.log` - LaTeX compilation logs

All log files use ISO 8601 timestamps.
