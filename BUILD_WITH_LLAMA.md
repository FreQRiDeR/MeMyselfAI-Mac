# 🚀 Building MeMyselfAI with Bundled llama-simple-chat

## What's Changed

The app now **bundles llama-simple-chat inside**! Users won't need to install llama.cpp separately.

---

## Quick Build (3 Steps)

```bash
# 1. Update the path in MeMyselfAI.spec (line 28)
# Change this line to YOUR llama-simple-chat location:
llama_binary_path = '/Users/terramoda/llama.cpp/build/bin/llama-simple-chat'

# 2. Make build script executable
chmod +x build_app.sh

# 3. Build!
./build_app.sh
```

**Result:** `dist/MeMyselfAI.app` with llama-simple-chat built-in!

---

## Files to Update in Your Project

Replace these files with the new bundled versions:

1. **MeMyselfAI.spec** → Project root
2. **backend/llama_wrapper.py** → Replace with `llama_wrapper_bundled.py`
3. **backend/config.py** → Replace with `config_bundled.py`
4. **build_app.sh** → Project root

---

## How It Works

### Before Build:
```
llama.cpp/build/bin/llama-simple-chat  ← Your local binary
```

### After Build:
```
MeMyselfAI.app/
└── Contents/
    └── MacOS/
        └── llama/
            └── llama-simple-chat  ← Bundled inside app!
```

### At Runtime:
- App detects it's running from bundle
- Automatically uses bundled llama-simple-chat
- No configuration needed for llama.cpp path!

---

## What Users Need

✅ **Bundled in app:**
- llama-simple-chat binary
- Your Python code
- PyQt6
- Python runtime

❌ **Users still need:**
- Model files (.gguf) - too large to bundle
- Configure models directory in Settings

---

## First Run Experience

**Without bundling:**
1. Open app
2. Configure llama.cpp path
3. Configure models directory
4. Add models
5. Start chatting

**With bundling (NEW):**
1. Open app
2. Configure models directory only
3. Add models
4. Start chatting ✨

---

## Build Steps Explained

```bash
./build_app.sh
```

This will:
1. ✅ Check PyInstaller is installed
2. ✅ Clean previous builds
3. ✅ Copy llama-simple-chat into app bundle
4. ✅ Bundle all Python code
5. ✅ Create MeMyselfAI.app
6. ✅ Verify llama-simple-chat is inside

---

## Verifying the Bundle

After building, check that llama-simple-chat is included:

```bash
# Check if binary is bundled
ls -lh dist/MeMyselfAI.app/Contents/MacOS/llama/

# Should show:
# llama-simple-chat  (executable)

# Test the app
open dist/MeMyselfAI.app
```

---

## App Size

- **Without llama.cpp:** ~50-100MB
- **With llama-simple-chat:** ~60-120MB
- **Still manageable!**

Models are NOT bundled (they're 500MB-8GB each), users provide their own.

---

## Distribution

### For Personal Use:
```bash
cp -r dist/MeMyselfAI.app /Applications/
```

### For Sharing with Others:

1. **Create DMG:**
```bash
# Install create-dmg
brew install create-dmg

# Create installer
create-dmg \
  --volname "MeMyselfAI" \
  --window-pos 200 120 \
  --window-size 800 400 \
  --icon-size 100 \
  --app-drop-link 600 185 \
  "MeMyselfAI-1.0.0.dmg" \
  "dist/MeMyselfAI.app"
```

2. **Sign the app (if you have Developer ID):**
```bash
codesign --deep --force --verify --verbose \
  --sign "Developer ID Application: Your Name" \
  dist/MeMyselfAI.app
```

3. **Notarize (optional, for Gatekeeper):**
```bash
xcrun altool --notarize-app \
  --primary-bundle-id "com.memyselfai.app" \
  --username "your@email.com" \
  --password "@keychain:AC_PASSWORD" \
  --file MeMyselfAI-1.0.0.dmg
```

---

## Troubleshooting

### ⚠️ "llama-simple-chat not found" during build

Check the path in `MeMyselfAI.spec` line 28:
```python
llama_binary_path = '/Users/terramoda/llama.cpp/build/bin/llama-simple-chat'
```

Verify it exists:
```bash
ls -la /Users/terramoda/llama.cpp/build/bin/llama-simple-chat
```

### ⚠️ "Permission denied" when running llama-simple-chat

Make sure it's executable:
```bash
chmod +x /Users/terramoda/llama.cpp/build/bin/llama-simple-chat
```

### ⚠️ App crashes on launch

Run from terminal to see errors:
```bash
./dist/MeMyselfAI.app/Contents/MacOS/MeMyselfAI
```

Check Console.app for crash logs.

### ⚠️ "App is damaged" message

Remove quarantine attribute:
```bash
xattr -cr dist/MeMyselfAI.app
```

---

## Advanced: Bundle a Model Too

If you want to bundle a small model (like TinyLlama ~500MB):

**1. Add to MeMyselfAI.spec:**
```python
# After line 24, add:
if Path('models/tinyllama.gguf').exists():
    data_files.append(('models/tinyllama.gguf', 'models'))
```

**2. Update config.py to set default model:**
```python
DEFAULT_CONFIG = {
    "llama_cpp_path": "bundled" if _is_bundled else "",
    "models_directory": "models" if _is_bundled else "",  # Use bundled models
    ...
}
```

**Result:** App is 600MB+ but works COMPLETELY out of the box!

---

## Next Steps

1. **Build the app:**
   ```bash
   ./build_app.sh
   ```

2. **Test it:**
   ```bash
   open dist/MeMyselfAI.app
   ```

3. **If it works, you're done!** 🎉

4. **Optional:** Create DMG, sign, and distribute

---

## Summary

✅ **What you get:**
- Fully self-contained app (except models)
- llama-simple-chat built-in
- One-click installation
- Works on any Mac (same architecture)

✅ **Users only need:**
- Download your app
- Add their model files
- Start chatting!

**Much better user experience!** 🚀
