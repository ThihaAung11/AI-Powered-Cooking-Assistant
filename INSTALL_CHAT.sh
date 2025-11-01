#!/bin/bash

echo "🚀 Installing Cooking Assistant Chat Dependencies..."

# Install dependencies
echo "📦 Installing Python packages..."
uv sync

# Check if .env exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env and add your OPENAI_API_KEY"
else
    echo "✅ .env file already exists"
fi

echo ""
echo "✅ Installation complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env and add your OPENAI_API_KEY"
echo "2. Run: uv run uvicorn app.main:app --reload"
echo "3. Visit: http://localhost:8000/docs"
echo ""
echo "📚 See CHAT_SETUP.md for API documentation"
