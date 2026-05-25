import time
from collections import deque # deque = buffer circular eficiente
import numpy as np
import pyqtgraph as pg # Librería de gráficas de alto desempeño que es más rápida que matplotlib
from pyqtgraph.Qt import QtWidgets, QtCore

class RealTimePlot(QtWidgets.QWidget):
    def __init__(self, recibirdatos):
       self.recibirdatos = recibirdatos
       self.app= QtWidgets.QApplication([])
       self.ventana=pg.GraphicsLayoutWidget(show=True, title="Gráfica en tiempo real")
       self.ventana.tamaño(1200, 600)
       self.ventana.setbackground('k') #Color de fondo
       self.plot = self.ventana.addPlot(title="Datos en tiempo real")

       self.plot.showGrid(x=True, y=True, alph=0.2) # Mostrar cuadrícula
       self.plot.setLabel('left', 'ADC')
       self.plot.setLabel('bottom', 'Tiempo', units='s')
       self.plot.addLegend() # Agregar leyenda
       self.curva.raw = self.plot.plot(pen=pg.mkPen(color='yellow', width=2), name="Señal ADC") # Curva para la señal ADC
       self.curva.filtrada= self.plot.plot(pen=pg.mkPen(color='purple', width=2), name="Señal Filtrada") # Curva para la señal filtrada
       self.ventana.show()
       self.empezar_tiempo = time.perf_counter()
       self.timer=QtCore.QTimer()
       self.timer.timeout.connect(self.actualizar_grafica)
       self.timer.start(100) # Actualizar cada 100 ms

    def update(self):
        with self.recibirdatos.lock:
            raw= np.array(self.recibirdatos.raw_datos)
            filtrado= np.array(self.recibirdatos.filtrados_datos)
            if len(raw) > 0:
                self.curva.raw.setData(raw)
                self.curva.filtrada.setData(filtrado)
                tiempo_transcurrido = time.perf_counter() - self.empezar_tiempo

            if tiempo_transcurrido > 0:
                sps=(self.recibirdatos.sps/tiempo_transcurrido)
                self.ventana.setTitle(f"Gráfica en tiempo real - SPS: {sps:.2f}")
                self.empezar_tiempo = time.perf_counter()

    def run(self):
        QtWidgets.QApplication.instance().exec_() 
                