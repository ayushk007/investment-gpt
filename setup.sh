#!/bin/bash

# Installation and Run Script for NSE Stock Analysis App

echo "🚀 NSE Stock Analysis App - Setup Script"
echo "=========================================="
echo ""

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "❌ uv is not installed. Please install uv from https://docs.astral.sh/uv/getting-started and retry."
    exit 1
fi

# Sync dependencies (creates .venv automatically)
echo "📦 Syncing dependencies with uv..."
uv sync

echo "✅ Environment ready (.venv managed by uv)"
echo ""

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cp .env.example .env
    echo "✅ .env file created. Please update it with your API keys if needed."
    echo ""
fi

echo "🎉 Setup complete!"
echo ""
echo "To run the app, execute:"
echo "  uv run streamlit run app.py -- --server.port=8502"
echo "  # or simply ./run.sh"
echo ""
