import struct
import threading
import time
from websocket import create_connection

class WebSocketReceiver:
    def __init__(self, url="ws://192.168.4.10:8080", vref=3.3, resolution=4095):
        self.ws = create_connection(url)
        print("Conectado al servidor WebSocket:", url)
        self.vref = vref
        self.resolution = resolution
        self.buffer = []
        self.latencias = []
        self.total_datos = 0
        self.lock = threading.Lock()
        self.running = True

    def recibir(self):
        while self.running:
            try:
                data = self.ws.recv()
                t0 = time.perf_counter()
                if isinstance(data, bytes):
                    samples = struct.unpack(f"<{len(data)//2}H", data)
                    voltajes = [s * (self.vref / self.resolution) for s in samples]
                    with self.lock:
                        self.buffer = voltajes
                        self.total_datos += len(voltajes)
                        self.latencias.append((time.perf_counter()-t0)*1000)
                else:
                    print("TXT:", data)
            except Exception as e:
                print("Error en recepción:", e)
                self.running = False

    def cerrar(self):
        self.running = False
        self.ws.close()