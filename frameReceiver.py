

from queue import Queue, Empty
import threading
from typing import Any, Optional, Tuple
import imagezmq


class FrameReceiver:
    def __init__(self) -> None:      
        self.queue = Queue(maxsize=10)
        self.stop = False
        self.worker_thread = threading.Thread(target=self._run, args=())
        self.worker_thread.daemon = True
        self.endpoint_info: Optional[Tuple[str, int]] = None
    
    def start(self) -> None:
        self.worker_thread.start()

    def is_worker_running(self) -> bool:
        return self.worker_thread.is_alive()

    def _run(self) -> None:
        if not self.endpoint_info:
            raise Exception("No endpoint info provided to connect to")
        receiver = imagezmq.ImageHub(f"tcp://{self.endpoint_info[0]}:{self.endpoint_info[1]}", REQ_REP=False)
        self.stop = False
        while not self.stop:
            data = receiver.recv_image()
            self.queue.put(data[1])
    
    def get_frame(self) -> Any:
        try:
            return self.queue.get(block = False)
        except Empty:
            return None
    
    def close_if_running(self) -> None:
        if self.is_worker_running():
            self.stop = True
            self.worker_thread.join()