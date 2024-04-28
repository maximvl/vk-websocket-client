from dataclasses import dataclass, asdict


@dataclass
class PingMessage:
    last_ping_at: int


@dataclass
class ChatMessage:
    username: str
    user_id: int
    message: str
