#!/bin/bash
# build_app.sh - Build MeMyselfAI.app with PyInstaller

set -e

echo "🔨 Building MeMyselfAI.app with PyInstaller"
echo "============================================"
echo ""

# Check if PyInstaller is installed
if ! command -v pyinstaller &> /dev/null; then
    echo "📦 Installing PyInstaller..."
    pip3 install pyinstaller
fi

# Make sure PyQt6 is installed
echo "📦 Checking PyQt6..."
pip3 install PyQt6 --upgrade

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf build dist

# Build the app
echo "🔨 Building application..."
pyinstaller MeMyselfAI.spec --clean --noconfirm

# Check if build was successful
if [ -d "dist/MeMyselfAI.app" ]; then
    echo ""
    echo "✅ Build successful!"
    echo ""
    
    # Verify llama-simple-chat is bundled
    if [ -f "dist/MeMyselfAI.app/Contents/MacOS/llama/llama-simple-chat" ]; then
        echo "✅ llama-simple-chat is bundled"
    else
        echo "⚠️  WARNING: llama-simple-chat NOT found in bundle!"
    fi
    
    echo ""
    echo "📦 Your app is ready at: dist/MeMyselfAI.app"
    echo ""
    echo "To test it:"
    echo "  open dist/MeMyselfAI.app"
    echo ""
    echo "To move it to Applications:"
    echo "  cp -r dist/MeMyselfAI.app /Applications/"
    echo ""
else
    echo ""
    echo "❌ Build failed!"
    echo "Check the output above for errors."
    exit 1
fi
