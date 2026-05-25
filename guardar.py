import csv

class CSVGuardar:
    def __init__(self, filename="datos_guardados.csv"):
        self.filename = filename
        with open(self.filename, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Index", "Voltaje (V)", "Filtrado (V)"])

    def guardar(self, raw, filtrado):
        with open(self.filename, "a", newline="") as f:
            writer = csv.writer(f)
            for i, (r, fval) in enumerate(zip(raw, filtrado)):
                writer.writerow([i, r, fval])