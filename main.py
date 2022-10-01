from typing import Tuple
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.widget import Widget
from kivy.uix.popup import Popup
from kivy.properties import ObjectProperty, ListProperty
from kivy.lang.builder import Builder
import cv2

from utils import Timer
from kivy.graphics.texture import Texture
from kivy.logger import Logger

from frameReceiver import FrameReceiver

main_content = Builder.load_file("detectionstream.kv")
BLACK_COLOR = [0, 0, 0, 1]
GREEN_COLOR = [.17, .745, .145, 1]
RED_COLOR = [.7, 0, 0, 1]


class ConnectionPopup(FloatLayout):
    popup = ObjectProperty(None)

class MainWindow(Widget):
    connect_label_color = ListProperty(BLACK_COLOR)

class DetectionStreamApp(App):
    def build(self) -> Widget:
        self.frame_receiver = FrameReceiver()
        #self.frame_receiver.start()
        self.frame_display_timer = Timer(1/30, self.show_frame)
        self.host_inactivity_timer = Timer(3, self.toggle_label_host_active, False)
        self.main_window = MainWindow()
        return self.main_window

    def on_connect(self, *args) -> None:
        connection_popup = ConnectionPopup()
        popupWindow = Popup(title="Connection to Motion Detector", content=connection_popup, size_hint=(None, None), size=(400, 300))
        connection_popup.popup = popupWindow
        popupWindow.open()

    def on_host_info_entered(self, ip_addr:str, port:int) -> None:
        if not self.host_info_changed((ip_addr, port)):
            return
        self.frame_receiver.close_if_running()
        self.frame_receiver.endpoint_info = (ip_addr, port)
        self.frame_receiver.start()
        self.toggle_label_host_active(True)
        self.frame_display_timer.start()
        self.host_inactivity_timer.start()
    
    def host_info_changed(self, host_info:Tuple[str , int]) -> None:
        if self.frame_receiver.endpoint_info and \
            host_info[0] == self.frame_receiver.endpoint_info[0] and \
            host_info[1] == self.frame_receiver.endpoint_info[1]:
            return False
        return True 

    def toggle_label_host_active(self, active: bool, *args) -> None:
        if active:
            self.main_window.connect_label_color = GREEN_COLOR
            self.main_window.ids.connected_label.text = f"Connected to host: {self.frame_receiver.endpoint_info[0]}:{self.frame_receiver.endpoint_info[1]}"
            return
        self.main_window.connect_label_color = RED_COLOR
        self.main_window.ids.connected_label.text = f"Inactivity detected on connection with host: {self.frame_receiver.endpoint_info[0]}:{self.frame_receiver.endpoint_info[1]}"  
        self.main_window.ids.canvas.texture = None

    def show_frame(self, *args) -> None:
        frame = self.frame_receiver.get_frame()
        if frame is None:
            if not self.host_inactivity_timer.isRunning():
                self.host_inactivity_timer.start()
            return
        self.host_inactivity_timer.stop()
        self.toggle_label_host_active(True)
        buffer = cv2.flip(frame, 0).tobytes()
        texture = Texture.create(size = (frame.shape[1], frame.shape[0]), colorfmt = "bgr")
        texture.blit_buffer(buffer, colorfmt = "bgr", bufferfmt= "ubyte")
        self.main_window.ids.canvas.texture = texture

if __name__ == "__main__":
    DetectionStreamApp().run()