import time
from vk_chat_reader.types import ChatMessage


class Storage:
    messages_by_ts: dict[int, list[ChatMessage]]
    messages_seen_by_reader: dict[str, set[int]]

    def __init__(self) -> None:
        self.messages_by_ts = {}
        self.messages_seen_by_reader = {}

    def add_messages(self, messages: list[ChatMessage]) -> None:
        for message in messages:
            self.messages_by_ts.setdefault(message['ts'], []).append(message)

    def get_unread_messages(self, reader: str, ts_from: int) -> list[ChatMessage]:
        messages = []
        self.messages_seen_by_reader.setdefault(reader, set())
        for ts, messages_list in self.messages_by_ts.items():
            if ts >= ts_from:
                for message in messages_list:
                    if message["id"] in self.messages_seen_by_reader[reader]:
                        continue
                    messages.append(message)
                    self.messages_seen_by_reader[reader].add(message["id"])
        return messages

    def reset_reader(self, reader: str) -> None:
        self.messages_seen_by_reader[reader] = set()

    def clear(self) -> None:
        self.messages_by_ts = {}
        self.messages_seen_by_reader = {}
