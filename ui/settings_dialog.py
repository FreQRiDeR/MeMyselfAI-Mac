"""
settings_dialog.py
Settings configuration dialog
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QPushButton, QLabel, QSpinBox,
    QDoubleSpinBox, QFileDialog, QDialogButtonBox,
    QGroupBox, QMessageBox, QFontComboBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from pathlib import Path


class SettingsDialog(QDialog):
    """Settings configuration dialog"""
    
    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config
        self.init_ui()
        self.load_settings()
    
    def init_ui(self):
        """Initialize UI"""
        self.setWindowTitle("Settings")
        self.setMinimumWidth(600)
        
        layout = QVBoxLayout(self)
        
        # Paths group
        paths_group = QGroupBox("Backend Configuration")
        paths_layout = QFormLayout()
        
        # Backend type selector
        from PyQt6.QtWidgets import QComboBox as QCombo
        self.backend_combo = QCombo()
        self.backend_combo.addItem("Local (llama.cpp)", "local")
        self.backend_combo.addItem("Ollama (Local API)", "ollama")
        self.backend_combo.addItem("HuggingFace (Cloud)", "huggingface")
        self.backend_combo.currentIndexChanged.connect(self.on_backend_changed)
        paths_layout.addRow("Backend:", self.backend_combo)
        
        # llama.cpp path (for local backend)
        self.llama_label = QLabel("llama.cpp Binary:")
        llama_layout = QHBoxLayout()
        self.llama_path_input = QLineEdit()
        self.llama_path_input.setPlaceholderText("bundled (or /path/to/llama-simple-chat)")
        llama_layout.addWidget(self.llama_path_input)
        
        self.browse_llama_btn = QPushButton("Browse...")
        self.browse_llama_btn.clicked.connect(self.browse_llama_path)
        llama_layout.addWidget(self.browse_llama_btn)
        
        paths_layout.addRow(self.llama_label, llama_layout)
        
        # Ollama URL (for ollama backend)
        self.ollama_label = QLabel("Ollama URL:")
        self.ollama_url_input = QLineEdit()
        self.ollama_url_input.setPlaceholderText("http://localhost:11434")
        paths_layout.addRow(self.ollama_label, self.ollama_url_input)
        
        # HuggingFace API Key (for HF backend)
        self.hf_label = QLabel("HF API Key:")
        self.hf_api_key_input = QLineEdit()
        self.hf_api_key_input.setPlaceholderText("hf_...")
        self.hf_api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        paths_layout.addRow(self.hf_label, self.hf_api_key_input)
        
        # Add note about models
        models_note = QLabel("💡 Models are managed via File → Manage Models")
        models_note.setStyleSheet("color: #666; font-style: italic;")
        paths_layout.addRow("", models_note)
        
        paths_group.setLayout(paths_layout)
        layout.addWidget(paths_group)
        
        # Generation parameters group
        params_group = QGroupBox("Generation Parameters")
        params_layout = QFormLayout()
        
        self.max_tokens_input = QSpinBox()
        self.max_tokens_input.setRange(1, 4096)
        self.max_tokens_input.setSingleStep(64)
        params_layout.addRow("Max Tokens:", self.max_tokens_input)
        
        self.temperature_input = QDoubleSpinBox()
        self.temperature_input.setRange(0.0, 2.0)
        self.temperature_input.setSingleStep(0.1)
        self.temperature_input.setDecimals(2)
        params_layout.addRow("Temperature:", self.temperature_input)
        
        self.context_size_input = QSpinBox()
        self.context_size_input.setRange(512, 8192)
        self.context_size_input.setSingleStep(512)
        params_layout.addRow("Context Size:", self.context_size_input)
        
        self.threads_input = QSpinBox()
        self.threads_input.setRange(1, 16)
        params_layout.addRow("Threads:", self.threads_input)
        
        params_group.setLayout(params_layout)
        layout.addWidget(params_group)
        
        # Appearance group
        appearance_group = QGroupBox("Appearance")
        appearance_layout = QFormLayout()
        
        self.font_family_input = QFontComboBox()
        self.font_family_input.setCurrentFont(QFont("SF Pro"))
        appearance_layout.addRow("Chat Font:", self.font_family_input)
        
        self.font_size_input = QSpinBox()
        self.font_size_input.setRange(8, 24)
        self.font_size_input.setValue(13)
        self.font_size_input.setSuffix(" pt")
        appearance_layout.addRow("Font Size:", self.font_size_input)
        
        appearance_group.setLayout(appearance_layout)
        layout.addWidget(appearance_group)
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.save_and_accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def load_settings(self):
        """Load current settings into UI"""
        # Load backend type
        backend_type = self.config.get("backend_type", "local")
        index = self.backend_combo.findData(backend_type)
        if index >= 0:
            self.backend_combo.setCurrentIndex(index)
        
        self.llama_path_input.setText(self.config.get("llama_cpp_path", ""))
        self.ollama_url_input.setText(self.config.get("ollama_url", "http://localhost:11434"))
        self.hf_api_key_input.setText(self.config.get("hf_api_key", ""))
        self.max_tokens_input.setValue(self.config.get("max_tokens", 512))
        self.temperature_input.setValue(self.config.get("temperature", 0.7))
        self.context_size_input.setValue(self.config.get("context_size", 2048))
        self.threads_input.setValue(self.config.get("threads", 4))
        
        # Appearance
        font_family = self.config.get("font_family", "SF Pro")
        self.font_family_input.setCurrentFont(QFont(font_family))
        self.font_size_input.setValue(self.config.get("font_size", 13))
        
        # Update visibility based on backend
        self.on_backend_changed()
    
    def on_backend_changed(self):
        """Handle backend type change - show/hide relevant fields"""
        backend = self.backend_combo.currentData()
        
        # Show/hide llama.cpp fields
        is_local = backend == "local"
        self.llama_label.setVisible(is_local)
        self.llama_path_input.setVisible(is_local)
        self.browse_llama_btn.setVisible(is_local)
        
        # Show/hide Ollama fields
        is_ollama = backend == "ollama"
        self.ollama_label.setVisible(is_ollama)
        self.ollama_url_input.setVisible(is_ollama)
        
        # Show/hide HuggingFace fields
        is_hf = backend == "huggingface"
        self.hf_label.setVisible(is_hf)
        self.hf_api_key_input.setVisible(is_hf)
    
    def browse_llama_path(self):
        """Browse for llama.cpp binary"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select llama.cpp Binary",
            "",
            "Executables (*)"
        )
        
        if file_path:
            self.llama_path_input.setText(file_path)
    
    def validate_settings(self) -> bool:
        """Validate settings before saving"""
        backend = self.backend_combo.currentData()
        
        if backend == "local":
            llama_path = self.llama_path_input.text().strip()
            
            # Allow 'bundled' as valid
            if llama_path == 'bundled':
                return True
            
            if not llama_path:
                QMessageBox.warning(self, "Invalid Settings", "Please specify llama.cpp binary path or use 'bundled'")
                return False
            
            if not Path(llama_path).exists():
                QMessageBox.warning(
                    self,
                    "Invalid Settings",
                    f"llama.cpp binary not found:\n{llama_path}\n\nTip: Use 'bundled' for the built-in version"
                )
                return False
        
        elif backend == "ollama":
            ollama_url = self.ollama_url_input.text().strip()
            if not ollama_url:
                QMessageBox.warning(self, "Invalid Settings", "Please specify Ollama URL")
                return False
            
            # Test connection
            from backend.unified_backend import UnifiedBackend
            if not UnifiedBackend.test_ollama_connection(ollama_url):
                reply = QMessageBox.question(
                    self,
                    "Ollama Not Running",
                    f"Cannot connect to Ollama at {ollama_url}\n\nSave anyway?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply != QMessageBox.StandardButton.Yes:
                    return False
        
        elif backend == "huggingface":
            api_key = self.hf_api_key_input.text().strip()
            if not api_key:
                QMessageBox.warning(self, "Invalid Settings", "Please specify HuggingFace API key")
                return False
            
            if not api_key.startswith('hf_'):
                QMessageBox.warning(self, "Invalid Settings", "HuggingFace API keys should start with 'hf_'")
                return False
        
        return True
    
    def save_and_accept(self):
        """Save settings and close dialog"""
        if not self.validate_settings():
            return
        
        # Save all settings
        self.config.set("backend_type", self.backend_combo.currentData())
        self.config.set("llama_cpp_path", self.llama_path_input.text().strip())
        self.config.set("ollama_url", self.ollama_url_input.text().strip())
        self.config.set("hf_api_key", self.hf_api_key_input.text().strip())
        self.config.set("max_tokens", self.max_tokens_input.value())
        self.config.set("temperature", self.temperature_input.value())
        self.config.set("context_size", self.context_size_input.value())
        self.config.set("threads", self.threads_input.value())
        self.config.set("font_family", self.font_family_input.currentFont().family())
        self.config.set("font_size", self.font_size_input.value())
        
        self.accept()