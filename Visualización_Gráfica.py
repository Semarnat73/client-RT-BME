import time
from collections import deque # deque = buffer circular eficiente
import numpy as np
import pyqtgraph as pg # Librería de gráficas de alto desempeño es más rápida que matplotlib
from pyqtgraph.Qt import QtWidgets, QtCore

class RealTimePlotter: #Creo la clase para visualizar la gráfica en tiempo real los datos del ADC
    def __init__(self,receiver,procesamiento,fs=1000,buffer_size=5000):
        self.receiver = receiver
        self.procesamiento = procesamiento
        self.fs = fs
        self.buffer_size = buffer_size
        self.raw_buffer = deque( # Buffer circular para señal ADC sin filtrar
            np.zeros(buffer_size),
            maxlen=buffer_size
        )

        self.filtered_buffer = deque(
            np.zeros(buffer_size),
            maxlen=buffer_size
        )

        self.app = QtWidgets.QApplication([]) # QApplication controla toda la interfaz gráfica
        self.window = pg.GraphicsLayoutWidget(
            title="ESP32-S3 ADC WebSocket"
        )
        self.window.resize(1300, 700)
        self.window.setBackground('k')

        self.plot = self.window.addPlot(title="Señal ADC Tiempo Real")
        self.plot.showGrid(x=True,y=True,alpha=0.3)
        self.plot.setLabel('left','ADC')
        self.plot.setLabel('bottom','Muestras')

        self.curve_raw = self.plot.plot(
            name="Sin filtrar",
            pen=pg.mkPen(
                color='yellow',
                width=2
            )
        )

        self.curve_filtered = self.plot.plot(
            name="Filtrada",
            pen=pg.mkPen(
                color='purple',
                width=2
            )
        )

        self.plot.addLegend()
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(10)
        self.window.show()
        self.start_time = time.perf_counter()

    def update(self):
        with self.receiver.lock: #Lock: sirve para asegurar que no se modifiquen los datos mientras se están leyendo
            raw_data = np.array(self.receiver.buffer)
            latency = np.array(self.receiver.latencias)
        if len(raw_data) == 0: #En caso de que no haya datos, sale de la función para evitar errores
            return
        filtered = self.procesamiento.procesar(
            raw_data
        )

        filtered = np.nan_to_num(filtered)
        self.raw_buffer.extend(raw_data)
        self.filtered_buffer.extend(filtered)
        raw_np = np.array(self.raw_buffer)

        filtered_np = np.array(self.filtered_buffer)

        self.curve_raw.setData(raw_np)

        self.curve_filtered.setData(filtered_np)

        fft = np.fft.fft(raw_np)
        frecuencia = np.fft.fftfreq(
            len(raw_np),
            d=1/self.fs #Tiempo entre muestras = 1/fs
        )

        indices = frecuencia > 0 
        frecuencia = frecuencia[indices]
        magnitud = np.abs(fft[indices])
        f_dom = frecuencia[
            np.argmax(magnitud)
        ]

        elapsed = (
            time.perf_counter()
            - self.start_time
        )

        if elapsed > 0: #Evita que se divida por cero en caso de que el tiempo transcurrido sea muy corto
            sps = (self.receiver.total_datos/ elapsed)

            lat_mean = np.mean(latency)

            self.window.setWindowTitle(f"ESP32-S3 ADC | "
                f"{sps:.1f} SPS | "
                f"Latencia: {lat_mean:.2f} ms | "
                f"Frec. Dominante: {f_dom:.2f} Hz"
            )

    def run(self):
        QtWidgets.QApplication.instance().exec()