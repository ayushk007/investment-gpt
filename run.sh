#!/bin/bash

# Run script for NSE Stock Analysis App

echo "🚀 Starting NSE Stock Analysis App..."
echo ""

# Ensure uv is installed
if ! command -v uv &> /dev/null; then
    echo "❌ uv is not installed. Please install uv from https://docs.astral.sh/uv/ and retry."
    exit 1
fi

# Sync dependencies (creates .venv automatically)
if [ ! -d ".venv" ]; then
    echo "📦 No .venv detected – running 'uv sync' to create environment..."
    uv sync
else
    echo "🔄 Refreshing dependencies via 'uv sync --frozen'..."
    uv sync --frozen
fi

# Run Streamlit app via uv
echo "🌐 Opening app at: http://localhost:8502"
echo ""
uv run streamlit run app.py -- --server.port=8502
