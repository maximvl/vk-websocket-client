from multiprocessing import Queue, Process
from queue import Empty
import time
from typing import Optional
from vk_chat_reader.types import ChatMessage, PingMessage

from vk_chat_reader.ws_client import start_websocket_client


class Controller:
    control_queue: Queue
    messages_queue: Queue
    worker: Optional[Process] = None

    def __init__(self) -> None:
        self.control_queue = Queue()
        self.messages_queue = Queue()

    def start_worker(self) -> None:
        if self.worker:
            if self.worker.is_alive():
                return
            self.worker.close()
            self.worker = None
        if self.control_queue is None:
            self.control_queue = Queue()
        if self.messages_queue is None:
            self.messages_queue = Queue()
        self.worker = Process(target=start_websocket_client, args=(self.control_queue, self.messages_queue))
        self.worker.start()

    def stop_worker(self) -> None:
        if self.worker is not None:
            self.worker.terminate()
            self.worker.join()
            self.worker.close()
            self.worker = None
            self.control_queue.close()
            self.messages_queue.close()

    def update_ping(self, ping_time: int) -> None:
        self.control_queue.put(PingMessage(ping_time))

    def read_all_messages(self) -> list[ChatMessage]:
        self.update_ping(int(time.time()))
        messages = []
        while True:
            try:
                messages.append(self.messages_queue.get_nowait())
            except Empty:
                break
        return messages
