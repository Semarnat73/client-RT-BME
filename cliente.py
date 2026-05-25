import threading
from captura import WebSocketReceiver   # clase para recibir datos
from procesar import Procesamiento      # clase para procesar datos
from graficar import RealTimePlotter    # clase para graficar
from guardar import CSVGuardar          # clase para guardar en CSV

class ClienteADC:
    def __init__(self, url="ws://192.168.4.10:8080"):
        # Conexión al ESP32-S3
        self.receiver = WebSocketReceiver(url)
        # Procesamiento con fs=500 (igual que tu firmware)
        self.proc = Procesamiento(fs=1000)
        # Guardado en CSV
        self.saver = CSVGuardar()
        # Gráfica en tiempo real
        self.plotter = RealTimePlotter(self.receiver, self.proc, fs=500)

    def iniciar(self):
        # Hilo de recepción de datos
        thread_rx = threading.Thread(target=self.receiver.recibir, daemon=True)
        thread_rx.start()

        # Ejecutar la gráfica en el hilo principal
        self.plotter.run()

    def guardar(self):
        # Guardar lote actual en CSV
        with self.receiver.lock:
            raw = self.receiver.buffer
        filtrado = self.proc.procesar(raw)
        self.saver.guardar(raw, filtrado)

if __name__ == "__main__":
    cliente = ClienteADC()
    cliente.iniciar()