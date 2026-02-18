<div align="center">
             <img src="/MeMyselfAi.png" width="400" />
             <h1>MeMyselfAi</h1>
</div>

# MeMyselfAI - macOS Desktop App

A native-feeling macOS chat application that wraps llama.cpp build.

## Features
- 💬 Clean chat interface
- 🤖 Local model support (uses llama.cpp)
- ☁️ Ollama Model Library integration. (Requires Ollama server to be running locally.)
- ⚡ Real-time streaming responses
- 📁 Model management
- 🎨 Native macOS look and feel

<div align="center">
             <img src="/window1.png" width="700" />
             
</div>

## Setup

### 1. Install Dependencies
```bash
pip3 install -r requirements.txt
```

### 2. Configure Your llama.cpp Path
Edit `config.json` and set:
```json
{
  "llama_cpp_path": "/path/to/your/llama.cpp/build/bin/llama-cli"
}
```

### 3. Add Your Models
Choose, Configure local models in Files/Manage Models.
Choose API, backend, and configure generation parameters in MeMyselfAi/Preferences

### 4. Run
```bash
python3 main.py
```

## Configuration

The app stores:
- **config.json** - App settings (llama.cpp path, model directory)
- **conversation_history.json** - Chat history (optional)

## Usage

1. Launch the app
2. Configure backend, generation parameters.
3. Select a model from the dropdown
4. Start chatting!
(Ollama integration requires Ollama-cli to be running and configured. 
Start Ollama with 'ollama serve and keep running in background.')

<div align="center">
             <img src="/window2.png" width="700" />

<div align="center">
             <img src="/window3.png" width="700" />

## Troubleshooting

**Model not loading?**
- Check llama.cpp path in config.json
- Verify model file exists and is readable
- Check terminal output for errors

**No response?**
- Ensure llama.cpp binary works: `./llama-cli --version`
- Check model format is GGUF
- Try a smaller model first

## Future Features
- [ ] Network server mode (DONE!)
- [ ] gRPC/WebSocket/HTTP+SSE support
- [ ] Multi-model support
- [ ] Conversation export
- [ ] System prompt templates


