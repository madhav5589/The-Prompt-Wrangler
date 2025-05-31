import json, os
from datetime import datetime
from typing import List, Dict
import streamlit as st

class ConversationManager:
    """Lightweight JSON persistence for extraction sessions."""
    FILE = "conversations.json"

    @classmethod
    def load_conversations(cls) -> List[Dict]:
        if os.path.exists(cls.FILE):
            try:
                with open(cls.FILE, "r") as f:
                    return json.load(f)
            except Exception as exc:
                st.error(f"Error loading conversations: {exc}")
        return []

    @classmethod
    def save_conversation(cls, conv: Dict):
        history = cls.load_conversations()
        conv["id"] = len(history) + 1
        conv["timestamp"] = datetime.now().isoformat()
        history.append(conv)
        try:
            with open(cls.FILE, "w") as f:
                json.dump(history, f, indent=2)
        except Exception as exc:
            st.error(f"Error saving conversation: {exc}")
