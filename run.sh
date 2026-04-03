#!/bin/bash
set -e

echo ""
echo "🧠 StockMind AI — Setup Script"
echo "================================"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.9+ from https://python.org"
    exit 1
fi

PYTHON_VER=$(python3 -c 'import sys; print(sys.version_info.minor)')
if [ "$PYTHON_VER" -lt 9 ]; then
    echo "❌ Python 3.9+ required. You have 3.${PYTHON_VER}"
    exit 1
fi

echo "✅ Python 3 found"

# Create and activate virtual environment
echo "📦 Creating virtual environment..."
cd backend
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies (this may take ~2 minutes)..."
pip install --upgrade pip -q
pip install -r requirements.txt -q

echo ""
echo "✅ Setup complete!"
echo ""
echo "🚀 Starting backend API on http://localhost:8000"
echo "🖥️  Open frontend/index.html in your browser"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start FastAPI
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
