from threading import Thread
import socket
from queue import Queue
from time import sleep

class PickByLightController(Thread):
    def __init__(self, message_queue: Queue, ip='<ESP-IP>', port=6454):
        super().__init__()
        self.ip = ip
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.running = True
        self.message_queue = message_queue
        
    def run(self):
        while self.running:
            try:
                if not self.message_queue.empty():
                    message = self.message_queue.get()
                    self.send_artnet(message)
                sleep(0.01)
            except Exception as e:
                print(f"ArtNet Error: {e}")
                
    def send_artnet(self, data):
        artnet_header = bytearray(b'Art-Net\0')
        opcode = bytearray([0x00, 0x50])
        version = bytearray([0x00, 0x0e])
        sequence = bytearray([0x00])
        physical = bytearray([0x00])
        universe = bytearray([0x00, 0x00])
        length = len(data).to_bytes(2, byteorder='big')
        
        packet = artnet_header + opcode + version + sequence + physical + universe + length + data
        self.socket.sendto(packet, (self.ip, self.port))

    def stop(self):
        self.running = False