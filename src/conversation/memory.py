from typing import List, Dict, Any


class ConversationMemory:
    """
    Minimal in-memory conversation state.
    Stores last N turns only.
    """

    def __init__(self, max_turns: int = 5):
        self.max_turns = max_turns
        self.history: List[Dict[str, Any]] = []

    def add_turn(self, user_message: str, agent_response: Dict[str, Any]):
        self.history.append({
            "user_message": user_message,
            "agent_response": agent_response
        })

        if len(self.history) > self.max_turns:
            self.history.pop(0)

    def get_context(self) -> List[Dict[str, Any]]:
        return self.history

    def clear(self):
        self.history = []