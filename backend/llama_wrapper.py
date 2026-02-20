"""
llama_wrapper.py
Wraps the existing llama.cpp binary for inference
"""

import sys
import subprocess
import threading
import queue
import json
from pathlib import Path
from typing import Optional, Callable, Generator


class LlamaWrapper:
    """Wrapper around llama.cpp CLI binary"""
    
    def __init__(self, llama_cpp_path: str):
        """
        Initialize the wrapper
        
        Args:
            llama_cpp_path: Path to llama-cli binary (or 'bundled' to use bundled version)
        """
        # Check if running from PyInstaller bundle and should use bundled version
        if llama_cpp_path == 'bundled' or (hasattr(sys, '_MEIPASS') and not llama_cpp_path):
            # Running from PyInstaller bundle - look for bundled llama-simple-chat
            if hasattr(sys, '_MEIPASS'):
                # Try multiple possible locations
                bundle_dir = sys._MEIPASS
                possible_paths = [
                    Path(bundle_dir) / 'llama' / 'llama-simple-chat',  # Expected location
                    Path(bundle_dir) / '../Frameworks/llama/llama-simple-chat',  # Frameworks dir
                ]
                
                bundled_path = None
                for path in possible_paths:
                    if path.exists():
                        bundled_path = path.resolve()
                        break
                
                if bundled_path:
                    self.llama_cpp_path = bundled_path
                    print(f"✅ Using bundled llama-simple-chat: {bundled_path}")
                else:
                    # If not found, construct expected path for error message
                    expected = Path(bundle_dir) / 'llama' / 'llama-simple-chat'
                    raise FileNotFoundError(
                        f"Bundled llama-simple-chat not found!\n"
                        f"Expected at: {expected}\n"
                        f"Bundle dir: {bundle_dir}\n"
                        f"Also checked: {[str(p) for p in possible_paths]}"
                    )
            else:
                raise FileNotFoundError("Not running from bundle, cannot use 'bundled' path")
        else:
            self.llama_cpp_path = Path(llama_cpp_path)
        
        self.process: Optional[subprocess.Popen] = None
        self.is_generating = False
        
        if not self.llama_cpp_path.exists():
            raise FileNotFoundError(f"llama.cpp not found at: {llama_cpp_path}")
    
    def check_model_file(self, model_path: str) -> bool:
        """Check if model file exists and is readable"""
        path = Path(model_path)
        return path.exists() and path.is_file() and path.suffix == '.gguf'
    
    def generate_streaming(
        self,
        model_path: str,
        prompt: str,
        max_tokens: int = 512,
        temperature: float = 0.7,
        callback: Optional[Callable[[str], None]] = None
    ) -> Generator[str, None, None]:
        """
        Generate response with streaming output
        
        Args:
            model_path: Path to .gguf model file
            prompt: User prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            callback: Optional callback for each token
            
        Yields:
            Generated tokens as they arrive
        """
        if not self.check_model_file(model_path):
            raise FileNotFoundError(f"Model not found: {model_path}")
        
        # Build command
        # Check if we're using llama-simple-chat (different args)
        binary_name = self.llama_cpp_path.name
        
        if 'simple-chat' in binary_name:
            # llama-simple-chat uses: -m model [-c context] [-ngl layers]
            # It reads prompt from stdin
            cmd = [
                str(self.llama_cpp_path),
                '-m', model_path,
                '-c', str(2048),
                '-ngl', '0',  # CPU only for now
            ]
            use_stdin_prompt = True
        else:
            # Standard llama-cli/llama-simple args
            cmd = [
                str(self.llama_cpp_path),
                '--model', model_path,
                '--prompt', f'User: {prompt}\nAssistant:',
                '--n-predict', str(max_tokens),
                '--temp', str(temperature),
                '--ctx-size', '2048',
                '--threads', '4',
                '--log-disable',
            ]
            use_stdin_prompt = False
        
        print(f"🚀 [LlamaWrapper] Running: {' '.join(cmd[:6])}...")
        
        try:
            self.is_generating = True
            
            # Start process
            self.process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=0
            )
            
            # If using llama-simple-chat, send prompt via stdin
            if use_stdin_prompt:
                try:
                    self.process.stdin.write(f'User: {prompt}\nAssistant:')
                    self.process.stdin.flush()
                    self.process.stdin.close()
                except Exception as e:
                    print(f"⚠️  [LlamaWrapper] Failed to write to stdin: {e}")
            else:
                # Close stdin for other binaries
                self.process.stdin.close()
            
            print("📡 [LlamaWrapper] Capturing output...")
            
            # SIMPLIFIED: Just skip obvious metadata, capture everything else
            skip_patterns = [
                'ggml_metal',
                'llama_model_loader',
                'llm_load_',
                'build =',
                'Loading model',
                '▄▄',  # ASCII art
                'available commands',
                '/exit',
                '/regen',
                '<|user|>',
                '<|assistant|>',
                '<|system|>',
                '<|end|>',
                '<|im_start|>',
                '<|im_end|>',
            ]
            
            capturing = False
            last_line = None  # Track last line to avoid duplicates
            
            for line in iter(self.process.stdout.readline, ''):
                if not line:
                    break
                
                # Skip metadata lines
                if any(pattern in line for pattern in skip_patterns):
                    continue
                
                # Skip blank lines at start
                if not capturing and not line.strip():
                    continue
                
                # Skip lines that are just dots (thinking animation)
                if line.strip().replace('.', '').strip() == '':
                    continue
                
                # Skip the prompt echo if it's there
                if 'User:' in line and 'Assistant:' not in line:
                    continue
                if line.strip() == 'Assistant:':
                    capturing = True
                    continue
                
                # Skip Bot: prefix (some models use this)
                if line.strip().startswith('Bot:'):
                    continue
                
                # Skip statistics
                if '[ Prompt:' in line or 't/s ]' in line:
                    break
                
                # Skip standalone > markers
                if line.strip() == '>':
                    continue
                
                # CAPTURE EVERYTHING ELSE
                if line.strip():
                    capturing = True
                    
                    # Strip ANSI color codes (like [32m, [33m, [0m)
                    import re
                    clean_line = re.sub(r'\x1b\[[0-9;]*m', '', line)
                    
                    # Remove leading > if present
                    clean_line = clean_line.lstrip('> ')
                    
                    # Remove chat template tokens
                    clean_line = clean_line.replace('<|user|>', '')
                    clean_line = clean_line.replace('<|assistant|>', '')
                    clean_line = clean_line.replace('<|system|>', '')
                    clean_line = clean_line.replace('<|end|>', '')
                    clean_line = clean_line.replace('<|im_start|>', '')
                    clean_line = clean_line.replace('<|im_end|>', '')
                    
                    # Remove "Bot:" prefix if present at start of line
                    if clean_line.strip().startswith('Bot:'):
                        clean_line = clean_line.replace('Bot:', '', 1).lstrip()
                    
                    # Skip if this line is just a repetition of what's already in last_line
                    current_stripped = clean_line.strip()
                    if current_stripped and last_line:
                        # Skip if this is identical to last line
                        if current_stripped == last_line:
                            continue
                        # Skip if this is just a subset/repeat of what was already said
                        if current_stripped in last_line or last_line in current_stripped:
                            # Only skip if they're very similar (one contains the other)
                            if len(current_stripped) < len(last_line) * 1.5:
                                continue
                    
                    last_line = current_stripped
                    
                    # Only yield if there's actual content
                    if clean_line.strip():
                        if callback:
                            callback(clean_line)
                        yield clean_line
            
            # Wait for completion
            self.process.wait()
            
            print(f"\n✅ [LlamaWrapper] Complete (exit code: {self.process.returncode})")
            
        except Exception as e:
            print(f"❌ [LlamaWrapper] Exception: {e}")
            raise
        finally:
            self.is_generating = False
            if self.process:
                try:
                    self.process.kill()
                except:
                    pass
                self.process = None
    
    def generate(
        self,
        model_path: str,
        prompt: str,
        max_tokens: int = 512,
        temperature: float = 0.7
    ) -> str:
        """
        Generate response (blocking, returns full response)
        
        Args:
            model_path: Path to .gguf model file
            prompt: User prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            
        Returns:
            Complete generated response
        """
        response = ""
        for token in self.generate_streaming(model_path, prompt, max_tokens, temperature):
            response += token
        return response.strip()
    
    def stop_generation(self):
        """Stop current generation"""
        if self.process and self.is_generating:
            print("🛑 [LlamaWrapper] Stopping generation...")
            try:
                self.process.terminate()
                self.process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                self.process.kill()
            finally:
                self.process = None
                self.is_generating = False


class ModelInfo:
    """Information about a model file"""
    
    def __init__(self, path: str):
        self.path = Path(path)
        self.name = self.path.stem
        self.size_mb = self.path.stat().st_size / (1024 * 1024)
        self.full_path = str(self.path.absolute())
    
    def __repr__(self):
        return f"ModelInfo(name='{self.name}', size={self.size_mb:.1f}MB)"


def discover_models(models_dir: str) -> list[ModelInfo]:
    """
    Discover all .gguf model files in a directory
    
    Args:
        models_dir: Directory to search
        
    Returns:
        List of ModelInfo objects
    """
    models_path = Path(models_dir)
    
    if not models_path.exists():
        print(f"⚠️  Models directory not found: {models_dir}")
        return []
    
    models = []
    for gguf_file in models_path.glob("**/*.gguf"):
        try:
            models.append(ModelInfo(str(gguf_file)))
        except Exception as e:
            print(f"⚠️  Failed to read model {gguf_file}: {e}")
    
    return sorted(models, key=lambda m: m.name)


if __name__ == "__main__":
    # Test the wrapper
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python llama_wrapper.py <llama-cli-path> <model-path>")
        sys.exit(1)
    
    wrapper = LlamaWrapper(sys.argv[1])
    
    print("Testing llama.cpp wrapper...")
    print(f"Binary: {wrapper.llama_cpp_path}")
    print(f"Model: {sys.argv[2]}")
    print("\nGenerating response...\n")
    
    response = wrapper.generate(
        model_path=sys.argv[2],
        prompt="What is the capital of France?",
        max_tokens=50
    )
    
    print(f"\n✅ Response: {response}")
