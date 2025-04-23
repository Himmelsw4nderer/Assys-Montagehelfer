from app import message_queue
from threading import Thread, Lock
import socket
from queue import Queue
import pyartnet
from time import sleep
from typing import List, Dict, Any, Optional

class PickByLightController(Thread):
    """
    Steuerklasse für Pick-by-Light Systeme mittels ArtNet-Protokoll.

    Verwendet pyartnet zur Kommunikation mit LED-Controllern (z.B. ESP32/ESP8266)
    und steuert WS2812B LED-Streifen für Pick-by-Light Anwendungen.
    """

    def __init__(self, message_queue: Queue, ip: str = '<ESP-IP>', port: int = 6454,
                led_count: int = 16, color: List[int] = [255, 255, 255], universe: int = 0) -> None:
        """
        Initialisiert den Pick-by-Light Controller.
        """
        super().__init__()
        self.ip = ip
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.running = True
        self.message_queue = message_queue
        self.color = color
        self.led_count = led_count
        self.universe = universe

        self.artnet: Optional[pyartnet.ArtNetNode] = None
        self.universe_obj: Any = None
        self.channel: Any = None
        self.led_values: List[int] = [0] * (led_count * 3)

        self._lock = Lock()

    def run(self) -> None:
        """
        Haupt-Thread-Methode, die das ArtNet-Setup initialisiert und die Schleife startet.
        """
        self.setup_artnet(self.ip, self.port, self.universe)
        while self.running:
            self.loop()

    def loop(self) -> None:
        """
        Hauptschleife des Controllers, die auf Nachrichten wartet und
        die entsprechenden LEDs steuert.
        """
        if message_queue.empty():
            return
        message: Dict[str, Any] = self.message_queue.get()
        position = message.get("position")
        # Convert position to integer
        if position is None:
            return
        try:
            position = int(position)
        except (ValueError, TypeError):
            print(f"Invalid position value: {position}")
            return
        else:
            print("No position provided")
            return
        try:
            self.set_all_leds()
            self.set_led(position, self.color)
        except Exception as e:
            print(f"Error setting LED: {e}")
        sleep(0.1)

    def set_led(self, position: int, color: List[int]) -> None:
        """
        Setzt eine einzelne LED auf die angegebene Farbe.

        Raises:
            ValueError: Wenn die Position ungültig ist oder der Channel nicht initialisiert wurde
        """
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

    def set_all_leds(self, color: List[int] = [0, 0, 0]) -> None:
        """
        Setzt alle LEDs auf die angegebene Farbe.
        Raises:
            ValueError: Wenn der Channel nicht initialisiert wurde
        """
        if self.channel is None:
            raise ValueError("Channel not initialized")
        with self._lock:
            for i in range(self.led_count):
                idx = i * 3
                self.led_values[idx] = color[0]
                self.led_values[idx + 1] = color[1]
                self.led_values[idx + 2] = color[2]
        self.channel.set_values(self.led_values)

    def setup_artnet(self, ip: str, port: int, universe: int) -> None:
        """
        Initialisiert die ArtNet-Verbindung.
        """
        self.artnet = pyartnet.ArtNetNode(ip, port)
        self.universe_obj = self.artnet.add_universe(universe)
        self.channel = self.universe_obj.add_channel(start=1, width=self.led_count * 3)
        self.channel.set_values([0] * (self.led_count * 3))

    def stop(self) -> None:
        """
        Stoppt den Controller und schaltet alle LEDs aus.
        """
        if self.channel:
            self.set_all_leds([0, 0, 0])
            sleep(0.1)

        self.running = False
