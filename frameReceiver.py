

from queue import Queue, Empty
import socket
import struct
import threading
from typing import Any, Optional, Tuple, Union


PAYLOAD_NUM_SIZE = struct.calcsize("I")
CHUNK_SIZE = 4096
FRAME_QUEUE_SIZE = 100
SOCEKT_TIMEOUT = 3

class FrameReceiver:
    def __init__(self) -> None:      
        self.queue = Queue(maxsize=FRAME_QUEUE_SIZE)
        self.running = False
        self.worker_thread: Optional[threading.Thread] = None
        self.endpoint_info: Optional[Tuple[str, int]] = None
    
    def start(self) -> None:
        self.close_if_running()
        self.set_new_worker_thread()
        self.worker_thread.start()
    
    def stop(self) -> None:
        self.running = False
        self.worker_thread.join()

    def set_new_worker_thread(self) -> None:
        self.worker_thread = threading.Thread(target=self._run, args=())
        self.worker_thread.daemon = True

    def is_worker_running(self) -> bool:
        return self.worker_thread.is_alive()

    def _run(self) -> None:
        if not self.endpoint_info:
            raise Exception("No endpoint info provided to connect to")
        try:  
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as conn_socket:
                conn_socket.settimeout(SOCEKT_TIMEOUT)
                conn_socket.connect((self.endpoint_info[0], int(self.endpoint_info[1])))
                self.running = True
                img_former = ImageFromBytesFormer(self.queue)
                while self.running:
                    data_bytes = conn_socket.recv(CHUNK_SIZE)
                    if not data_bytes:
                        break
                    img_former.process_chunk(data_bytes)
        except Exception as e:
            self.queue.put(e)
            self.running = False

    def get_frame(self) -> Optional[Union[bytes, Exception]]:
        try:
            return self.queue.get(block = False)
        except Empty:
            return None
    
    def is_running(self) -> bool:
        return self.running
    
    def close_if_running(self) -> None:
        if self.worker_thread and self.is_worker_running():
            self.running = False
            self.worker_thread.join()
            
class ImageFromBytesFormer:
    def __init__(self, queue: Queue) -> None:
        self.buffer = bytearray()
        self.size: Optional[int] = None
        self.queue = queue
        self.print_first = False

    def process_chunk(self, chunk: bytes) -> None:
        self.buffer.extend(chunk)
        if not self.size:
            if len(self.buffer) < PAYLOAD_NUM_SIZE:
                return
            self.size = struct.unpack("I", bytes(self.buffer[:PAYLOAD_NUM_SIZE]))[0]
            if not self.print_first:
                self.print_first = True
            del self.buffer[:PAYLOAD_NUM_SIZE]
        if len(self.buffer) < self.size:
            return
        frame_data = self.buffer[:self.size]
        self.queue.put(bytes(frame_data))
        del self.buffer[:self.size]
        self.size = None
    