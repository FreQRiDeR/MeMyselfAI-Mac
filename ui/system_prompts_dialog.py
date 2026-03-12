"""
system_prompts_dialog.py
UI for managing and selecting system prompts
"""

from PyQt6.QtWidgets import (
    QDialog, QHBoxLayout, QVBoxLayout, QListWidget, QListWidgetItem,
    QPushButton, QLabel, QLineEdit, QTextEdit, QMessageBox, QFrame,
    QInputDialog
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from backend.system_prompts import SystemPromptManager, SystemPrompt


class SystemPromptsDialog(QDialog):
    """
    Two-panel dialog:
      Left  – list of prompts (built-ins + custom)
      Right – editor / preview for selected prompt
    """

    prompt_selected = pyqtSignal(str)   # emits prompt_id when Apply clicked

    def __init__(self, manager: SystemPromptManager, parent=None):
        super().__init__(parent)
        self.manager    = manager
        self._selected_id = manager.active_id
        self._dirty     = False          # unsaved edits in editor

        self.setWindowTitle("System Prompts")
        self.setMinimumSize(780, 520)
        self._build_ui()
        self._populate_list()
        self._select_by_id(self._selected_id)

    # ── Build UI ──────────────────────────────
    def _build_ui(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── LEFT panel ────────────────────────
        left = QFrame()
        left.setFixedWidth(220)
        left.setStyleSheet("QFrame { background: #1C1C1E; border-right: 1px solid #3A3A3C; }")
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(0)

        # Header
        hdr = QLabel("  System Prompts")
        hdr.setFixedHeight(44)
        hdr.setStyleSheet(
            "background: #2C2C2E; color: #F2F2F7; font-size: 14px; font-weight: 600;"
            "border-bottom: 1px solid #3A3A3C;")
        left_layout.addWidget(hdr)

        # List
        self.prompt_list = QListWidget()
        self.prompt_list.setStyleSheet("""
            QListWidget {
                background: transparent; border: none; outline: none;
            }
            QListWidget::item {
                padding: 10px 14px;
                border-bottom: 1px solid #2C2C2E;
                color: #EBEBF5; font-size: 13px;
            }
            QListWidget::item:selected {
                background: #3A3A3C; color: #FFFFFF; border-radius: 4px;
            }
            QListWidget::item:hover:!selected { background: #2C2C2E; }
        """)
        self.prompt_list.currentItemChanged.connect(self._on_list_selection_changed)
        left_layout.addWidget(self.prompt_list, stretch=1)

        # Bottom buttons
        btn_row = QHBoxLayout()
        btn_row.setContentsMargins(8, 6, 8, 8)
        btn_row.setSpacing(6)

        self.new_btn = QPushButton("＋ New")
        self.del_btn = QPushButton("🗑")
        self.del_btn.setFixedWidth(32)

        for btn in (self.new_btn, self.del_btn):
            btn.setStyleSheet("""
                QPushButton {
                    background: #3A3A3C; color: #F2F2F7;
                    border: none; border-radius: 6px;
                    padding: 5px 10px; font-size: 12px;
                }
                QPushButton:hover { background: #48484A; }
                QPushButton:disabled { color: #6C6C6E; }
            """)

        self.new_btn.clicked.connect(self._new_prompt)
        self.del_btn.clicked.connect(self._delete_prompt)
        btn_row.addWidget(self.new_btn)
        btn_row.addWidget(self.del_btn)
        left_layout.addLayout(btn_row)

        root.addWidget(left)

        # ── RIGHT panel ───────────────────────
        right = QFrame()
        right.setStyleSheet("QFrame { background: #141414; }")
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(20, 16, 20, 16)
        right_layout.setSpacing(10)

        # Icon + Name row
        meta_row = QHBoxLayout()

        icon_label = QLabel("Icon:")
        icon_label.setStyleSheet("color: #8E8E93; font-size: 12px;")
        meta_row.addWidget(icon_label)

        self.icon_input = QLineEdit()
        self.icon_input.setFixedWidth(48)
        self.icon_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.icon_input.setFont(QFont("SF Pro", 16))
        self.icon_input.setStyleSheet("""
            QLineEdit {
                background: #2C2C2E; color: #F2F2F7;
                border: 1px solid #3A3A3C; border-radius: 6px; padding: 4px;
            }
        """)
        self.icon_input.textChanged.connect(lambda: self._mark_dirty())
        meta_row.addWidget(self.icon_input)
        meta_row.addSpacing(12)

        name_label = QLabel("Name:")
        name_label.setStyleSheet("color: #8E8E93; font-size: 12px;")
        meta_row.addWidget(name_label)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Prompt name…")
        self.name_input.setStyleSheet("""
            QLineEdit {
                background: #2C2C2E; color: #F2F2F7;
                border: 1px solid #3A3A3C; border-radius: 6px;
                padding: 6px 10px; font-size: 13px;
            }
            QLineEdit:focus { border-color: #e009a7; }
        """)
        self.name_input.textChanged.connect(lambda: self._mark_dirty())
        meta_row.addWidget(self.name_input, stretch=1)

        right_layout.addLayout(meta_row)

        # Prompt text
        prompt_label = QLabel("System Prompt:")
        prompt_label.setStyleSheet("color: #8E8E93; font-size: 12px;")
        right_layout.addWidget(prompt_label)

        self.prompt_edit = QTextEdit()
        self.prompt_edit.setFont(QFont("SF Mono", 13))
        self.prompt_edit.setPlaceholderText("Enter your system prompt here…")
        self.prompt_edit.setStyleSheet("""
            QTextEdit {
                background: #2C2C2E; color: #F2F2F7;
                border: 1px solid #3A3A3C; border-radius: 8px;
                padding: 10px; font-size: 13px; line-height: 1.5;
            }
            QTextEdit:focus { border-color: #e009a7; }
        """)
        self.prompt_edit.textChanged.connect(self._mark_dirty)
        right_layout.addWidget(self.prompt_edit, stretch=1)

        # Bottom buttons
        action_row = QHBoxLayout()

        self.save_btn = QPushButton("💾  Save")
        self.duplicate_btn = QPushButton("⎘  Duplicate")
        self.apply_btn = QPushButton("✅  Use This Prompt")
        self.cancel_btn = QPushButton("Cancel")

        self.apply_btn.setStyleSheet("""
            QPushButton {
                background: #e009a7; color: #FFFFFF;
                border: none; border-radius: 8px;
                padding: 8px 20px; font-size: 13px; font-weight: 600;
            }
            QPushButton:hover { background: #c0088f; }
        """)

        for btn in (self.save_btn, self.duplicate_btn, self.cancel_btn):
            btn.setStyleSheet("""
                QPushButton {
                    background: #3A3A3C; color: #F2F2F7;
                    border: none; border-radius: 8px;
                    padding: 8px 16px; font-size: 13px;
                }
                QPushButton:hover { background: #48484A; }
                QPushButton:disabled { color: #6C6C6E; }
            """)

        self.save_btn.clicked.connect(self._save_current)
        self.duplicate_btn.clicked.connect(self._duplicate_prompt)
        self.apply_btn.clicked.connect(self._apply_prompt)
        self.cancel_btn.clicked.connect(self.reject)

        action_row.addWidget(self.save_btn)
        action_row.addWidget(self.duplicate_btn)
        action_row.addStretch()
        action_row.addWidget(self.cancel_btn)
        action_row.addWidget(self.apply_btn)
        right_layout.addLayout(action_row)

        root.addWidget(right, stretch=1)

    # ── List helpers ──────────────────────────
    def _populate_list(self):
        self.prompt_list.clear()
        for sp in self.manager.all():
            item = QListWidgetItem(sp.display_name)
            item.setData(Qt.ItemDataRole.UserRole, sp.id)
            # Mark active
            if sp.id == self.manager.active_id:
                item.setText(sp.display_name + "  ✓")
            self.prompt_list.addItem(item)

    def _select_by_id(self, prompt_id: str):
        for i in range(self.prompt_list.count()):
            item = self.prompt_list.item(i)
            if item.data(Qt.ItemDataRole.UserRole) == prompt_id:
                self.prompt_list.setCurrentItem(item)
                return

    def _on_list_selection_changed(self, current, previous):
        if not current:
            return

        # Warn if there are unsaved edits
        if self._dirty:
            reply = QMessageBox.question(
                self, "Unsaved Changes",
                "You have unsaved changes. Discard them?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply != QMessageBox.StandardButton.Yes:
                self.prompt_list.blockSignals(True)
                self.prompt_list.setCurrentItem(previous)
                self.prompt_list.blockSignals(False)
                return

        prompt_id = current.data(Qt.ItemDataRole.UserRole)
        sp = self.manager.get(prompt_id)
        if not sp:
            return

        self._selected_id = prompt_id
        self._dirty = False

        # Populate right panel
        self.icon_input.setText(sp.icon)
        self.name_input.setText(sp.name)
        self.prompt_edit.setPlainText(sp.prompt)

        # Everything is editable - built-ins included
        self.icon_input.setReadOnly(False)
        self.name_input.setReadOnly(False)
        self.prompt_edit.setReadOnly(False)
        self.save_btn.setEnabled(True)
        self.del_btn.setEnabled(True)

        self._dirty = False   # reset after populating

    # ── Actions ───────────────────────────────
    def _mark_dirty(self):
        self._dirty = True

    def _save_current(self):
        name   = self.name_input.text().strip()
        icon   = self.icon_input.text().strip() or "💬"
        prompt = self.prompt_edit.toPlainText().strip()

        if not name:
            QMessageBox.warning(self, "Validation", "Please enter a name.")
            return
        if not prompt:
            QMessageBox.warning(self, "Validation", "Please enter a prompt.")
            return

        self.manager.update(self._selected_id, name, icon, prompt)
        self._dirty = False
        self._populate_list()
        self._select_by_id(self._selected_id)
        self.status_flash("✅  Saved!")

    def _new_prompt(self):
        sp = self.manager.add(
            name="New Prompt",
            icon="💬",
            prompt="You are a helpful assistant."
        )
        self._populate_list()
        self._select_by_id(sp.id)

    def _duplicate_prompt(self):
        original = self.manager.get(self._selected_id)
        if not original:
            return
        sp = self.manager.add(
            name=f"{original.name} (copy)",
            icon=original.icon,
            prompt=original.prompt
        )
        self._populate_list()
        self._select_by_id(sp.id)

    def _delete_prompt(self):
        sp = self.manager.get(self._selected_id)
        if not sp:
            return

        # Check if this is an overridden built-in
        original_builtin = next(
            (p for p in __import__('backend.system_prompts', fromlist=['BUILTIN_PROMPTS']).BUILTIN_PROMPTS
             if p['id'] == self._selected_id), None
        )

        if original_builtin:
            reply = QMessageBox.question(
                self, "Delete Prompt",
                f'Delete "{sp.name}"?\n\nThis will remove it from the list entirely.',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
        else:
            reply = QMessageBox.question(
                self, "Delete Prompt", f'Delete "{sp.name}"?',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

        if reply == QMessageBox.StandardButton.Yes:
            self.manager.delete(self._selected_id)
            self._selected_id = self.manager.active_id
            self._dirty = False
            self._populate_list()
            self._select_by_id(self._selected_id)

    def _apply_prompt(self):
        self.manager.set_active(self._selected_id)
        self.prompt_selected.emit(self._selected_id)
        self._populate_list()
        self.accept()

    def status_flash(self, msg: str):
        """Briefly show a message in the window title."""
        self.setWindowTitle(f"System Prompts — {msg}")
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(2000, lambda: self.setWindowTitle("System Prompts"))