# 🚀 MeMyselfAI - Quick Start Guide

## What You Just Got

A fully functional macOS desktop chat app that wraps your existing llama.cpp build!

## Project Structure

```
MeMyselfAI-Mac/
├── main.py                    # ← Run this to start the app
├── setup_and_run.sh          # ← Or run this (handles setup automatically)
├── config.json               # Configuration file
├── requirements.txt          # Python dependencies
├── backend/
│   ├── llama_wrapper.py     # Wraps your llama.cpp binary
│   └── config.py            # Configuration management
├── ui/
│   ├── main_window.py       # Main application window
│   └── settings_dialog.py   # Settings UI
└── README.md                 # Full documentation
```

## Quick Start (3 Steps!)

### Step 1: Install Dependencies

```bash
cd /path/to/MeMyselfAI-Mac
pip3 install -r requirements.txt
```

**Or use the automated script:**
```bash
./setup_and_run.sh
```

### Step 2: Configure Paths

When you first run the app, you'll see a settings dialog. Configure:

1. **llama.cpp Binary Path**
   - Point to: `/path/to/llama.cpp/build/bin/llama-cli`
   - This is the binary you already compiled!

2. **Models Directory**
   - Point to where your `.gguf` models are
   - Example: `~/models` or `/path/to/llama.cpp/models`

### Step 3: Chat!

1. Select a model from the dropdown
2. Type a message
3. Press Enter or click Send
4. Watch the response stream in real-time! ✨

## Running the App

### Option 1: Automated (Recommended)
```bash
./setup_and_run.sh
```

### Option 2: Manual
```bash
python3 main.py
```

### Option 3: With Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 main.py
```

## Features You Get Out of the Box

✅ **Real-time streaming responses** - See tokens as they're generated
✅ **Model management** - Switch between models easily
✅ **Clean macOS-native UI** - Feels like a real Mac app
✅ **Conversation history** - Scroll back through your chat
✅ **Stop generation** - Cancel if it's taking too long
✅ **Settings panel** - Adjust temperature, max tokens, etc.
✅ **Keyboard shortcuts** - Cmd+K to clear, Cmd+Q to quit

## Configuration Options

Edit `config.json` or use Settings dialog:

```json
{
  "llama_cpp_path": "/path/to/llama-cli",
  "models_directory": "/path/to/models",
  "max_tokens": 512,           // How many tokens to generate
  "temperature": 0.7,           // 0.0-2.0, higher = more creative
  "context_size": 2048,         // Context window size
  "threads": 4                  // CPU threads to use
}
```

## Testing Your Setup

### Test 1: Check llama.cpp Works
```bash
/path/to/llama.cpp/build/bin/llama-cli --version
```
Should output version info.

### Test 2: Test the Wrapper Directly
```bash
cd backend
python3 llama_wrapper.py /path/to/llama-cli /path/to/model.gguf
```
Should generate a response to "What is the capital of France?"

### Test 3: Run the Full App
```bash
python3 main.py
```

## Troubleshooting

### "llama.cpp not found"
- Check the path in Settings
- Make sure you're pointing to `llama-cli` (not `llama-server` or folder)
- Test: `ls -la /path/to/llama-cli` should show the file

### "No models found"
- Check models directory in Settings
- Make sure models are `.gguf` files
- Test: `ls /path/to/models/*.gguf` should list models

### "Generation fails"
- Try a smaller model first (like TinyLlama)
- Check terminal output for error messages
- Reduce `max_tokens` in Settings

### "App won't start"
- Check Python version: `python3 --version` (need 3.10+)
- Install dependencies: `pip3 install -r requirements.txt`
- Check for errors in terminal

## What Your Models Should Look Like

```
~/models/
├── tinyllama-1.1b-chat-v1.0.Q2_K.gguf         # 483 MB
├── Llama-3.2-1B-Instruct-RLHF-v0.1-Q4_K_M.gguf # 808 MB
└── phi-2-Q4_K_M.gguf                           # 1.5 GB
```

Any `.gguf` file will be auto-discovered!

## Next Steps

Once this works, we can add:
- 🌐 Network server mode (so iOS app can connect)
- 📡 gRPC/WebSocket/HTTP+SSE protocols
- 💾 Save conversation history
- 🎨 Custom themes
- 🔧 System prompts and templates

## Need Help?

1. Check terminal output for error messages
2. Test llama.cpp directly: `./llama-cli --help`
3. Verify paths in `config.json`
4. Try the test scripts in backend/

## Success Checklist

- [ ] Dependencies installed (`pip3 install -r requirements.txt`)
- [ ] llama.cpp path configured
- [ ] Models directory configured
- [ ] At least one `.gguf` model available
- [ ] App launches without errors
- [ ] Model appears in dropdown
- [ ] Sending message generates response

**If all checked, you're good to go! 🎉**

## What Makes This Better Than iOS?

✅ **Actually works** - No crashes, no API incompatibilities
✅ **Uses your working build** - The llama.cpp you already compiled
✅ **Easy to debug** - Python errors are readable
✅ **Fast iteration** - Change code, run again, instant feedback
✅ **Foundation for iOS** - Once this works, iOS connects as client

---

**Ready to start? Run:**
```bash
./setup_and_run.sh
```

**Or:**
```bash
python3 main.py
```

**Let me know when you have it running!** 🚀
