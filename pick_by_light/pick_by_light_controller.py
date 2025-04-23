from app import message_queue
from threading import Thread, Lock
import socket
from queue import Queue
import pyartnet
from time import sleep

class PickByLightController(Thread):
    def __init__(self, message_queue: Queue, ip='<ESP-IP>', port=6454, led_count=16, color=[255,255,255], universe=0):
        super().__init__()
        self.ip = ip
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.running = True
        self.message_queue = message_queue
        self.color = color
        self.led_count = led_count
        self.universe = universe

        self.artnet = None
        self.universe_obj = None
        self.channel = None
        self.led_values = [0] * (led_count * 3)

        self._lock = Lock()

    def run(self) -> None:
        self.setup_artnet(self.ip, self.port, self.universe)
        while self.running:
            self.loop()

    def loop(self):
        if message_queue.empty():
            return
        message = self.message_queue.get()
        position = message.get("position")
        try:
            self.set_all_leds()
            self.set_led(position, self.color)
        except Exception as e:
            print(f"Error setting LED: {e}")
        sleep(0.1)

    def set_led(self, position: int, color: list):
        if not(0 <= position < self.led_count):
            raise ValueError("Invalid position")
        if self.channel is None:
            raise ValueError("Channel not initialized")
        with self._lock:
            idx = position * 3

            self.led_values[idx] = color[0]
            self.led_values[idx + 1] = color[1]
            self.led_values[idx + 2] = color[2]

            self.channel.set_values(self.led_values)

    def set_all_leds(self, color=[0, 0, 0]):
        if self.channel is None:
            raise ValueError("Channel not initialized")
        with self._lock:
            for i in range(self.led_count):
                idx = i * 3
                self.led_values[idx] = color[0]
                self.led_values[idx + 1] = color[1]
                self.led_values[idx + 2] = color[2]
        self.channel.set_values(self.led_values)

    def setup_artnet(self, ip: str, port: int, universe: int):
        self.artnet = pyartnet.ArtNetNode(ip, port)
        self.universe_obj = self.artnet.add_universe(universe)
        self.channel = self.universe_obj.add_channel(start=1, width=self.led_count * 3)
        self.channel.set_values([0] * (self.led_count * 3))


    def stop(self):
        """Stoppt den Controller und schaltet alle LEDs aus."""
        if self.channel:
            self.set_all_leds([0, 0, 0])
            sleep(0.1)

        self.running = False
