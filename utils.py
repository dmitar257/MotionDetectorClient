from typing import Callable, Optional
from kivy.clock import Clock
from functools import partial

class Timer:
    def __init__(self, interval: int, callback_func: Callable, *args) -> None:   
        self.interval = interval
        self.callback = callback_func
        self.clock = None
        self.args = args
        self.is_running = False
    
    def start(self) -> None:
        self.stop()
        self.clock = Clock.schedule_interval(partial(self.callback, *self.args), self.interval)
        self.is_running = True
    
    def stop(self) -> None:
        if not self.clock is None:
            self.clock.cancel()
        self.is_running = False
    
    def isRunning(self) -> bool:
        return self.is_running

