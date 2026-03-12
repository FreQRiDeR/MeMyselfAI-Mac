"""
chat_history.py
Manages saving and loading chat conversations
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Optional


def get_history_dir() -> Path:
    """Get platform-appropriate directory for chat history"""
    if getattr(sys, 'frozen', False):
        if sys.platform == 'darwin':
            history_dir = Path.home() / 'Library' / 'Application Support' / 'MeMyselfAI' / 'chats'
        else:
            history_dir = Path.home() / '.memyselfai' / 'chats'
    else:
        history_dir = Path('.') / 'chats'

    history_dir.mkdir(parents=True, exist_ok=True)
    return history_dir


class ChatMessage:
    def __init__(self, role: str, content: str, timestamp: str = None):
        self.role = role        # 'user' or 'assistant'
        self.content = content
        self.timestamp = timestamp or datetime.now().isoformat()

    def to_dict(self):
        return {"role": self.role, "content": self.content, "timestamp": self.timestamp}

    @classmethod
    def from_dict(cls, data):
        return cls(role=data['role'], content=data['content'], timestamp=data.get('timestamp', ''))


class Conversation:
    def __init__(self, title: str = None, model: str = None):
        self.id = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
        self.title = title or "New Conversation"
        self.model = model or ""
        self.created_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()
        self.messages: List[ChatMessage] = []

    def add_message(self, role: str, content: str):
        self.messages.append(ChatMessage(role, content))
        self.updated_at = datetime.now().isoformat()
        # Auto-title from first user message
        if role == 'user' and self.title == "New Conversation":
            self.title = content[:50] + ("..." if len(content) > 50 else "")

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "model": self.model,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "messages": [m.to_dict() for m in self.messages]
        }

    @classmethod
    def from_dict(cls, data):
        conv = cls.__new__(cls)
        conv.id = data['id']
        conv.title = data['title']
        conv.model = data.get('model', '')
        conv.created_at = data['created_at']
        conv.updated_at = data.get('updated_at', data['created_at'])
        conv.messages = [ChatMessage.from_dict(m) for m in data.get('messages', [])]
        return conv

    @property
    def formatted_date(self) -> str:
        try:
            dt = datetime.fromisoformat(self.updated_at)
            now = datetime.now()
            if dt.date() == now.date():
                return f"Today {dt.strftime('%I:%M %p')}"
            elif (now.date() - dt.date()).days == 1:
                return f"Yesterday {dt.strftime('%I:%M %p')}"
            else:
                return dt.strftime('%b %d, %Y')
        except:
            return self.updated_at[:10]


class ChatHistory:
    def __init__(self):
        self.history_dir = get_history_dir()

    def save(self, conversation: Conversation):
        filepath = self.history_dir / f"{conversation.id}.json"
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(conversation.to_dict(), f, indent=2, ensure_ascii=False)

    def load(self, conversation_id: str) -> Optional[Conversation]:
        filepath = self.history_dir / f"{conversation_id}.json"
        if not filepath.exists():
            return None
        with open(filepath, 'r', encoding='utf-8') as f:
            return Conversation.from_dict(json.load(f))

    def delete(self, conversation_id: str) -> bool:
        filepath = self.history_dir / f"{conversation_id}.json"
        if filepath.exists():
            filepath.unlink()
            return True
        return False

    def all(self) -> List[Conversation]:
        conversations = []
        for filepath in self.history_dir.glob('*.json'):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    conversations.append(Conversation.from_dict(json.load(f)))
            except Exception as e:
                print(f"⚠️  Failed to load {filepath.name}: {e}")
        conversations.sort(key=lambda c: c.updated_at, reverse=True)
        return conversations