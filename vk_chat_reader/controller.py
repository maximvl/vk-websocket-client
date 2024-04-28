from multiprocessing import Queue, Process
import time
from typing import Optional
from vk_chat_reader.types import PingMessage

from vk_chat_reader.ws_client import start_websocket_client


class Controller:
    queue: Queue
    worker: Optional[Process] = None

    def __init__(self) -> None:
        self.queue = Queue()

    def start_worker(self) -> None:
        if self.worker:
            if self.worker.is_alive():
                return
            self.worker.close()
            self.worker = None
        self.worker = Process(target=start_websocket_client, args=(self.queue,))
        self.worker.start()

    def stop_worker(self) -> None:
        if self.worker is not None:
            self.worker.terminate()
            self.worker.join()
            self.worker.close()
            self.worker = None

    def update_ping(self, ping_time: int) -> None:
        self.queue.put(PingMessage(ping_time))
