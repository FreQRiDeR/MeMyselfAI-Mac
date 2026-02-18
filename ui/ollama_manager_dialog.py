"""
ollama_manager_dialog.py
Ollama Model Manager - Browse, download, and manage Ollama models
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget,
    QPushButton, QLabel, QListWidget, QListWidgetItem,
    QProgressBar, QLineEdit, QMessageBox, QTextEdit,
    QWidget, QGroupBox, QFormLayout
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont
import requests
import json
from typing import List, Dict, Optional


class ModelPullThread(QThread):
    """Thread for pulling Ollama models with progress"""
    
    progress = pyqtSignal(str, int, int)  # status, completed, total
    finished = pyqtSignal(bool, str)  # success, message
    
    def __init__(self, ollama_url: str, model_name: str):
        super().__init__()
        self.ollama_url = ollama_url
        self.model_name = model_name
        self._stop = False
    
    def run(self):
        """Pull model with progress updates"""
        try:
            response = requests.post(
                f'{self.ollama_url}/api/pull',
                json={"name": self.model_name},
                stream=True,
                timeout=None
            )
            response.raise_for_status()
            
            for line in response.iter_lines():
                if self._stop:
                    break
                    
                if line:
                    try:
                        data = json.loads(line)
                        status = data.get('status', '')
                        completed = data.get('completed', 0)
                        total = data.get('total', 0)
                        
                        self.progress.emit(status, completed, total)
                        
                        if status == 'success':
                            self.finished.emit(True, f"Successfully pulled {self.model_name}")
                            return
                            
                    except json.JSONDecodeError:
                        continue
            
            if not self._stop:
                self.finished.emit(True, f"Successfully pulled {self.model_name}")
                
        except Exception as e:
            self.finished.emit(False, f"Failed to pull model: {e}")
    
    def stop(self):
        """Stop the pull operation"""
        self._stop = True


class OllamaLibraryTab(QWidget):
    """Tab for browsing and pulling models from Ollama library"""
    
    # Popular Ollama models with descriptions
    POPULAR_MODELS = [
        # Cloud Models (Instant, Run on Ollama servers)
        {
            "name": "qwen3-coder:480b-cloud",
            "size": "Cloud",
            "description": "☁️ Qwen3 Coder 480B - Massive coding model (Cloud)",
            "tags": ["cloud", "code", "huge", "recommended"],
            "is_cloud": True
        },
        {
            "name": "gpt-oss:120b-cloud",
            "size": "Cloud",
            "description": "☁️ GPT-OSS 120B - Large model (Cloud)",
            "tags": ["cloud", "chat", "huge"],
            "is_cloud": True
        },
        {
            "name": "gpt-oss:20b-cloud",
            "size": "Cloud",
            "description": "☁️ GPT-OSS 20B - Medium model (Cloud)",
            "tags": ["cloud", "chat"],
            "is_cloud": True
        },
        {
            "name": "qwen3-vl:235b-cloud",
            "size": "Cloud",
            "description": "☁️ Qwen3 Vision 235B - Multimodal (Cloud)",
            "tags": ["cloud", "vision", "huge"],
            "is_cloud": True
        },
        {
            "name": "minimax-m2:cloud",
            "size": "Cloud",
            "description": "☁️ MiniMax M2 - Advanced model (Cloud)",
            "tags": ["cloud", "chat"],
            "is_cloud": True
        },
        {
            "name": "glm-4.6:cloud",
            "size": "Cloud",
            "description": "☁️ GLM 4.6 - ChatGLM (Cloud)",
            "tags": ["cloud", "chat", "multilingual"],
            "is_cloud": True
        },
        # Local Models (Download to your disk)
        {
            "name": "llama2",
            "size": "3.8 GB",
            "description": "Meta's Llama 2 - Great all-around model",
            "tags": ["chat", "general", "popular"],
            "is_cloud": False
        },
        {
            "name": "llama2:13b",
            "size": "7.3 GB",
            "description": "Llama 2 13B - Better quality, slower",
            "tags": ["chat", "general", "large"],
            "is_cloud": False
        },
        {
            "name": "mistral",
            "size": "4.1 GB",
            "description": "Mistral 7B - Excellent performance",
            "tags": ["chat", "general", "popular"],
            "is_cloud": False
        },
        {
            "name": "codellama",
            "size": "3.8 GB",
            "description": "Code Llama - Specialized for coding",
            "tags": ["code", "programming"],
            "is_cloud": False
        },
        {
            "name": "phi",
            "size": "1.6 GB",
            "description": "Microsoft Phi - Small and fast",
            "tags": ["small", "fast", "recommended"],
            "is_cloud": False
        },
        {
            "name": "gemma:2b",
            "size": "1.4 GB",
            "description": "Google Gemma 2B - Tiny and quick",
            "tags": ["small", "fast", "recommended"],
            "is_cloud": False
        },
        {
            "name": "gemma:7b",
            "size": "4.8 GB",
            "description": "Google Gemma 7B - Good quality",
            "tags": ["chat", "general"],
            "is_cloud": False
        },
        {
            "name": "qwen:7b",
            "size": "4.4 GB",
            "description": "Qwen 7B - Multilingual support",
            "tags": ["multilingual", "chat"],
            "is_cloud": False
        },
        {
            "name": "neural-chat",
            "size": "4.1 GB",
            "description": "Intel Neural Chat - Optimized for CPU",
            "tags": ["chat", "cpu-optimized"],
            "is_cloud": False
        },
        {
            "name": "starling-lm",
            "size": "4.1 GB",
            "description": "Starling - High quality responses",
            "tags": ["chat", "quality"],
            "is_cloud": False
        }
    ]
    
    def __init__(self, ollama_url: str, parent=None):
        super().__init__(parent)
        self.ollama_url = ollama_url
        self.pull_thread = None
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout(self)
        
        # Search box
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Search:"))
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Filter models...")
        self.search_box.textChanged.connect(self.filter_models)
        search_layout.addWidget(self.search_box)
        layout.addLayout(search_layout)
        
        # Recommended models
        rec_label = QLabel("💡 Recommendations:")
        rec_label.setStyleSheet("color: #007AFF; font-weight: bold; margin-top: 10px;")
        layout.addWidget(rec_label)
        
        rec_text = QLabel(
            "☁️ Cloud (Instant, Powerful): qwen3-coder:480b-cloud, gpt-oss:120b-cloud\n"
            "💾 Local Small (Fast on CPU): phi, gemma:2b | Local Medium: llama2, mistral"
        )
        rec_text.setStyleSheet("color: #666; font-style: italic; margin-bottom: 10px;")
        layout.addWidget(rec_text)
        
        # Model list
        self.model_list = QListWidget()
        self.model_list.itemDoubleClicked.connect(self.on_model_double_clicked)
        layout.addWidget(self.model_list)
        
        # Populate list
        self.populate_models()
        
        # Pull button and progress
        button_layout = QHBoxLayout()
        
        self.pull_button = QPushButton("Pull Selected Model")
        self.pull_button.clicked.connect(self.pull_selected_model)
        button_layout.addWidget(self.pull_button)
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.cancel_pull)
        self.cancel_button.setVisible(False)
        button_layout.addWidget(self.cancel_button)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Status label
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #666; font-style: italic;")
        layout.addWidget(self.status_label)
    
    def populate_models(self):
        """Populate the model list"""
        self.model_list.clear()
        
        for model in self.POPULAR_MODELS:
            item = QListWidgetItem()
            
            # Add cloud icon for cloud models
            is_cloud = model.get('is_cloud', False)
            icon = "☁️ " if is_cloud else "💾 "
            
            # Format: Icon Name (Size) - Description
            text = f"{icon}{model['name']:<30} ({model['size']:<8}) - {model['description']}"
            item.setText(text)
            item.setData(Qt.ItemDataRole.UserRole, model['name'])
            item.setData(Qt.ItemDataRole.UserRole + 1, is_cloud)  # Store cloud flag
            
            # Highlight recommended models in green
            if 'recommended' in model['tags']:
                font = item.font()
                font.setBold(True)
                item.setFont(font)
                item.setForeground(Qt.GlobalColor.darkGreen)
            # Highlight cloud models in blue
            elif is_cloud:
                font = item.font()
                font.setBold(True)
                item.setFont(font)
                item.setForeground(Qt.GlobalColor.blue)
            
            self.model_list.addItem(item)
    
    def filter_models(self, text: str):
        """Filter models based on search text"""
        text = text.lower()
        
        for i in range(self.model_list.count()):
            item = self.model_list.item(i)
            should_show = text in item.text().lower()
            item.setHidden(not should_show)
    
    def on_model_double_clicked(self, item: QListWidgetItem):
        """Handle double-click on model"""
        self.pull_selected_model()
    
    def pull_selected_model(self):
        """Pull the selected model"""
        current_item = self.model_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "No Selection", "Please select a model to pull")
            return
        
        model_name = current_item.data(Qt.ItemDataRole.UserRole)
        is_cloud = current_item.data(Qt.ItemDataRole.UserRole + 1)
        
        # Different messages for cloud vs local
        if is_cloud:
            message = (
                f"Add cloud model {model_name}?\n\n"
                "☁️ This is a CLOUD model:\n"
                "• Instant setup (no download)\n"
                "• Runs on Ollama's servers\n"
                "• Requires internet to use\n"
                "• Free during beta\n"
                "• Can be HUGE (480B!)"
            )
        else:
            message = (
                f"Download {model_name}?\n\n"
                "💾 This is a LOCAL model:\n"
                "• Will download to your disk\n"
                "• Runs on your Mac Pro\n"
                "• Works offline after download\n"
                "• May take several minutes"
            )
        
        # Confirm
        reply = QMessageBox.question(
            self,
            "Pull Model",
            message,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        # Start pull
        self.pull_button.setEnabled(False)
        self.cancel_button.setVisible(True)
        self.progress_bar.setVisible(not is_cloud)  # Hide progress for cloud models
        self.progress_bar.setValue(0)
        
        status_msg = f"Adding {model_name}..." if is_cloud else f"Downloading {model_name}..."
        self.status_label.setText(status_msg)
        
        self.pull_thread = ModelPullThread(self.ollama_url, model_name)
        self.pull_thread.progress.connect(self.on_pull_progress)
        self.pull_thread.finished.connect(self.on_pull_finished)
        self.pull_thread.start()
    
    def on_pull_progress(self, status: str, completed: int, total: int):
        """Handle pull progress updates"""
        if total > 0:
            percent = int((completed / total) * 100)
            self.progress_bar.setValue(percent)
            
            # Format sizes
            completed_mb = completed / (1024 * 1024)
            total_mb = total / (1024 * 1024)
            self.status_label.setText(f"{status}: {completed_mb:.1f} MB / {total_mb:.1f} MB ({percent}%)")
        else:
            self.status_label.setText(status)
    
    def on_pull_finished(self, success: bool, message: str):
        """Handle pull completion"""
        self.pull_button.setEnabled(True)
        self.cancel_button.setVisible(False)
        self.progress_bar.setVisible(False)
        
        if success:
            self.status_label.setText(f"✅ {message}")
            QMessageBox.information(self, "Success", message)
        else:
            self.status_label.setText(f"❌ {message}")
            QMessageBox.critical(self, "Error", message)
    
    def cancel_pull(self):
        """Cancel the current pull"""
        if self.pull_thread and self.pull_thread.isRunning():
            self.pull_thread.stop()
            self.pull_thread.wait()
            self.on_pull_finished(False, "Pull cancelled")


class OllamaDownloadedTab(QWidget):
    """Tab for managing downloaded models"""
    
    def __init__(self, ollama_url: str, parent=None):
        super().__init__(parent)
        self.ollama_url = ollama_url
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout(self)
        
        # Info
        info_label = QLabel("Downloaded Models:")
        info_label.setFont(QFont("SF Pro", 13, QFont.Weight.Bold))
        layout.addWidget(info_label)
        
        # Model list
        self.model_list = QListWidget()
        layout.addWidget(self.model_list)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.refresh_button = QPushButton("🔄 Refresh")
        self.refresh_button.clicked.connect(self.refresh_models)
        button_layout.addWidget(self.refresh_button)
        
        self.delete_button = QPushButton("🗑️ Delete Selected")
        self.delete_button.clicked.connect(self.delete_selected)
        button_layout.addWidget(self.delete_button)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        # Status
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #666; font-style: italic;")
        layout.addWidget(self.status_label)
        
        # Load models
        self.refresh_models()
    
    def refresh_models(self):
        """Refresh the list of downloaded models"""
        self.model_list.clear()
        self.status_label.setText("Loading...")
        
        try:
            response = requests.get(f'{self.ollama_url}/api/tags', timeout=5)
            response.raise_for_status()
            data = response.json()
            
            models = data.get('models', [])
            
            if not models:
                self.status_label.setText("No models downloaded yet")
                return
            
            for model in models:
                name = model.get('name', 'unknown')
                size = model.get('size', 0)
                
                # Detect cloud models (size = 0 or very small)
                is_cloud = size == 0 or ':cloud' in name.lower() or '-cloud' in name.lower()
                
                item = QListWidgetItem()
                
                if is_cloud:
                    # Cloud model
                    icon = "☁️ "
                    size_text = "Cloud"
                    item.setText(f"{icon}{name:<40} ({size_text})")
                    item.setForeground(Qt.GlobalColor.blue)
                else:
                    # Local model
                    icon = "💾 "
                    size_gb = size / (1024 * 1024 * 1024)
                    size_text = f"{size_gb:.2f} GB"
                    item.setText(f"{icon}{name:<40} ({size_text})")
                
                item.setData(Qt.ItemDataRole.UserRole, name)
                item.setData(Qt.ItemDataRole.UserRole + 1, is_cloud)
                
                self.model_list.addItem(item)
            
            cloud_count = sum(1 for m in models if m.get('size', 0) == 0 or ':cloud' in m.get('name', '').lower())
            local_count = len(models) - cloud_count
            
            self.status_label.setText(f"Found {len(models)} model(s) - {cloud_count} cloud, {local_count} local")
            
        except Exception as e:
            self.status_label.setText(f"❌ Error: {e}")
            QMessageBox.critical(self, "Error", f"Failed to fetch models:\n{e}")
    
    def delete_selected(self):
        """Delete the selected model"""
        current_item = self.model_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "No Selection", "Please select a model to delete")
            return
        
        model_name = current_item.data(Qt.ItemDataRole.UserRole)
        is_cloud = current_item.data(Qt.ItemDataRole.UserRole + 1)
        
        # Different messages for cloud vs local
        if is_cloud:
            message = (
                f"Remove cloud model {model_name}?\n\n"
                "☁️ This will:\n"
                "• Remove it from your list (instant)\n"
                "• You can re-add it anytime (free)\n"
                "• No disk space freed (it's cloud)"
            )
        else:
            message = (
                f"Delete {model_name}?\n\n"
                "💾 This will:\n"
                "• Delete it from your disk\n"
                "• Free up disk space\n"
                "• Require re-download to use again"
            )
        
        # Confirm
        reply = QMessageBox.question(
            self,
            "Delete Model",
            message,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        # Delete
        try:
            response = requests.delete(
                f'{self.ollama_url}/api/delete',
                json={"name": model_name},
                timeout=10
            )
            response.raise_for_status()
            
            action = "Removed" if is_cloud else "Deleted"
            QMessageBox.information(self, "Success", f"{action} {model_name}")
            self.refresh_models()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to delete model:\n{e}")


class OllamaManagerDialog(QDialog):
    """Main Ollama Model Manager dialog"""
    
    def __init__(self, ollama_url: str = 'http://localhost:11434', parent=None):
        super().__init__(parent)
        self.ollama_url = ollama_url
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI"""
        self.setWindowTitle("Ollama Model Manager")
        self.setMinimumSize(800, 600)
        
        layout = QVBoxLayout(self)
        
        # Header
        header = QLabel("Ollama Model Manager")
        header.setFont(QFont("SF Pro", 18, QFont.Weight.Bold))
        header.setStyleSheet("color: #007AFF; margin-bottom: 10px;")
        layout.addWidget(header)
        
        # Connection status
        self.status_label = QLabel()
        self.check_ollama_status()
        layout.addWidget(self.status_label)
        
        # Tabs
        tabs = QTabWidget()
        
        # Library tab
        self.library_tab = OllamaLibraryTab(self.ollama_url, self)
        tabs.addTab(self.library_tab, "📚 Model Library")
        
        # Downloaded tab
        self.downloaded_tab = OllamaDownloadedTab(self.ollama_url, self)
        tabs.addTab(self.downloaded_tab, "💾 Downloaded")
        
        layout.addWidget(tabs)
        
        # Close button
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        layout.addWidget(close_button)
    
    def check_ollama_status(self):
        """Check if Ollama is running"""
        try:
            response = requests.get(f'{self.ollama_url}/api/tags', timeout=2)
            if response.status_code == 200:
                self.status_label.setText(f"✅ Connected to Ollama at {self.ollama_url}")
                self.status_label.setStyleSheet("color: green;")
            else:
                self.show_ollama_error()
        except:
            self.show_ollama_error()
    
    def show_ollama_error(self):
        """Show Ollama connection error"""
        self.status_label.setText(f"❌ Cannot connect to Ollama at {self.ollama_url}")
        self.status_label.setStyleSheet("color: red;")
        
        QMessageBox.warning(
            self,
            "Ollama Not Running",
            f"Cannot connect to Ollama at {self.ollama_url}\n\n"
            "Make sure Ollama is installed and running:\n"
            "1. Install: brew install ollama\n"
            "2. Start: ollama serve\n\n"
            "Visit https://ollama.ai for more info."
        )
    
    def showEvent(self, event):
        """Refresh when dialog is shown"""
        super().showEvent(event)
        self.downloaded_tab.refresh_models()


if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    import sys
    
    app = QApplication(sys.argv)
    dialog = OllamaManagerDialog()
    dialog.exec()