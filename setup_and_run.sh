#!/bin/bash
# setup_and_run.sh
# Setup and run MeMyselfAI

set -e

echo "🚀 MeMyselfAI Setup & Run Script"
echo "================================"
echo ""

# Check Python version
echo "📍 Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.10 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | awk '{print $2}')
echo "✅ Found Python $PYTHON_VERSION"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
    echo ""
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install/upgrade dependencies
echo "📥 Installing dependencies..."
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt

echo "✅ Dependencies installed"
echo ""

# Check configuration
echo "⚙️  Checking configuration..."
if [ ! -f "config.json" ]; then
    echo "⚠️  No config.json found, creating default..."
    cat > config.json << 'EOF'
{
  "llama_cpp_path": "",
  "models_directory": "",
  "default_model": "",
  "max_tokens": 512,
  "temperature": 0.7,
  "context_size": 2048,
  "threads": 4,
  "save_conversations": true,
  "theme": "system"
}
EOF
fi

echo "✅ Configuration ready"
echo ""

# Run application
echo "🎨 Launching MeMyselfAI..."
echo ""
python3 main.py

# Deactivate venv on exit
deactivate
