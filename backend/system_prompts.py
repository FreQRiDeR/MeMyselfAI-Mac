"""
system_prompts.py
Manages system prompts - storage, selection, built-in presets
"""

import json
import sys
from pathlib import Path
from typing import List, Optional


def get_prompts_file() -> Path:
    if getattr(sys, 'frozen', False):
        if sys.platform == 'darwin':
            d = Path.home() / 'Library' / 'Application Support' / 'MeMyselfAI'
        else:
            d = Path.home() / '.memyselfai'
    else:
        d = Path('.')
    d.mkdir(parents=True, exist_ok=True)
    return d / 'system_prompts.json'


# ── Built-in presets ──────────────────────────────────────────────────────────
BUILTIN_PROMPTS = [
    {
        "id": "default",
        "name": "Default Assistant",
        "icon": "🤖",
        "prompt": "You are a helpful, harmless, and honest AI assistant.",
        "builtin": True
    },
    {
        "id": "concise",
        "name": "Concise",
        "icon": "⚡",
        "prompt": (
            "You are a helpful assistant. Keep your answers short and to the point. "
            "Avoid unnecessary explanation. Use bullet points when listing items."
        ),
        "builtin": True
    },
    {
        "id": "creative",
        "name": "Creative Writer",
        "icon": "✍️",
        "prompt": (
            "You are a creative writing partner with a flair for vivid language, "
            "engaging storytelling, and imaginative ideas. Embrace metaphor, tone, "
            "and narrative structure. Be expressive and original."
        ),
        "builtin": True
    },
    {
        "id": "coder",
        "name": "Senior Developer",
        "icon": "💻",
        "prompt": (
            "You are a senior software engineer. When writing code: prefer clarity over "
            "cleverness, include concise inline comments, handle edge cases, and follow "
            "best practices for the language in use. If asked to review code, give "
            "actionable, specific feedback."
        ),
        "builtin": True
    },
    {
        "id": "tutor",
        "name": "Patient Tutor",
        "icon": "🎓",
        "prompt": (
            "You are a patient, encouraging tutor. Break complex topics into digestible "
            "steps, use analogies and examples, check for understanding, and celebrate "
            "progress. Adapt your explanation style to the learner's level."
        ),
        "builtin": True
    },
    {
        "id": "socratic",
        "name": "Socratic Coach",
        "icon": "🧠",
        "prompt": (
            "You help people think through problems themselves rather than just giving "
            "answers. Ask clarifying questions, highlight assumptions, and guide the "
            "user toward their own insight. Only provide direct answers when explicitly asked."
        ),
        "builtin": True
    },
    {
        "id": "professional",
        "name": "Professional Editor",
        "icon": "📝",
        "prompt": (
            "You are a professional editor and writing coach. Review text for clarity, "
            "grammar, tone, and structure. Suggest improvements with brief explanations. "
            "Maintain the author's voice while elevating the writing."
        ),
        "builtin": True
    },
    {
        "id": "devil",
        "name": "Devil's Advocate",
        "icon": "😈",
        "prompt": (
            "You challenge ideas constructively by arguing the opposite position, "
            "exposing weak assumptions, and stress-testing logic. Be rigorous but fair. "
            "Your goal is to strengthen thinking, not win arguments."
        ),
        "builtin": True
    },
]


class SystemPrompt:
    def __init__(self, id: str, name: str, icon: str, prompt: str, builtin: bool = False):
        self.id      = id
        self.name    = name
        self.icon    = icon
        self.prompt  = prompt
        self.builtin = builtin

    def to_dict(self):
        return {"id": self.id, "name": self.name, "icon": self.icon,
                "prompt": self.prompt, "builtin": self.builtin}

    @classmethod
    def from_dict(cls, d):
        return cls(id=d['id'], name=d['name'], icon=d.get('icon', '💬'),
                   prompt=d['prompt'], builtin=d.get('builtin', False))

    @property
    def display_name(self):
        return f"{self.icon}  {self.name}"


class SystemPromptManager:
    def __init__(self):
        self._file = get_prompts_file()
        self._custom: List[SystemPrompt] = []
        self._active_id: str = "default"
        self._load()

    # ── Persistence ───────────────────────────
    def _load(self):
        if not self._file.exists():
            self._custom = []
            self._active_id = "default"
            return
        try:
            data = json.loads(self._file.read_text(encoding='utf-8'))
            self._active_id = data.get('active_id', 'default')
            self._custom = [SystemPrompt.from_dict(p)
                            for p in data.get('custom', [])
                            if not p.get('builtin')]
        except Exception as e:
            print(f"⚠️  Failed to load system prompts: {e}")
            self._custom = []
            self._active_id = "default"

    def _save(self):
        data = {
            "active_id": self._active_id,
            "custom": [p.to_dict() for p in self._custom]
        }
        self._file.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')

    # ── Public API ────────────────────────────
    def all(self) -> List[SystemPrompt]:
        """Return all prompts - custom overrides replace built-ins with same id."""
        custom_ids = {p.id for p in self._custom}
        builtins = [SystemPrompt.from_dict(p) for p in BUILTIN_PROMPTS
                    if p['id'] not in custom_ids]
        return builtins + self._custom

    def get(self, prompt_id: str) -> Optional[SystemPrompt]:
        for p in self.all():
            if p.id == prompt_id:
                return p
        return None

    @property
    def active(self) -> SystemPrompt:
        p = self.get(self._active_id)
        return p if p else SystemPrompt.from_dict(BUILTIN_PROMPTS[0])

    @property
    def active_id(self) -> str:
        return self._active_id

    def set_active(self, prompt_id: str):
        self._active_id = prompt_id
        self._save()

    def add(self, name: str, icon: str, prompt: str) -> SystemPrompt:
        import uuid
        sp = SystemPrompt(
            id=f"custom_{uuid.uuid4().hex[:8]}",
            name=name, icon=icon, prompt=prompt, builtin=False
        )
        self._custom.append(sp)
        self._save()
        return sp

    def update(self, prompt_id: str, name: str, icon: str, prompt: str) -> bool:
        # Update existing custom entry
        for p in self._custom:
            if p.id == prompt_id:
                p.name   = name
                p.icon   = icon
                p.prompt = prompt
                self._save()
                return True
        # Override a built-in by adding it to custom list
        original = next((p for p in BUILTIN_PROMPTS if p['id'] == prompt_id), None)
        if original:
            sp = SystemPrompt(id=prompt_id, name=name, icon=icon, prompt=prompt, builtin=False)
            self._custom.append(sp)
            self._save()
            return True
        return False

    def delete(self, prompt_id: str) -> bool:
        before = len(self._custom)
        self._custom = [p for p in self._custom if p.id != prompt_id]
        deleted_custom = len(self._custom) < before

        # Also handle deleting a built-in (store as "deleted" marker)
        is_builtin = any(p['id'] == prompt_id for p in BUILTIN_PROMPTS)

        if deleted_custom or is_builtin:
            if is_builtin and not deleted_custom:
                # Mark built-in as deleted by adding a tombstone
                tombstone = SystemPrompt(
                    id=prompt_id, name="__deleted__",
                    icon="", prompt="", builtin=False
                )
                self._custom.append(tombstone)

            if self._active_id == prompt_id:
                # Find first non-deleted prompt
                remaining = [p for p in self.all() if p.name != "__deleted__" and p.id != prompt_id]
                self._active_id = remaining[0].id if remaining else "default"

            self._save()
            return True
        return False

    def reset_builtin(self, prompt_id: str) -> bool:
        """Restore a built-in prompt to its original state."""
        self._custom = [p for p in self._custom if p.id != prompt_id]
        self._save()
        return True