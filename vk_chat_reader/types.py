from dataclasses import dataclass
from typing import TypedDict


@dataclass
class PingMessage:
    last_ping_at: int


class ChatMessage(TypedDict):
    id: int
    username: str
    user_id: int
    message: str
    ts: int
