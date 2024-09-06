import argparse
from time import sleep
import tkinter as tk
from tkinter import messagebox
import clases as segmentator

class MemorySimulatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulador de Segmentación de Memoria")

        # Variables de la interfaz
        self.memory_var = tk.IntVar()
        self.process_var = tk.IntVar()

        # Etiquetas y campos de entrada
        tk.Label(root, text="Memoria Total (Bytes):").grid(row=0, column=0, padx=10, pady=10)
        tk.Entry(root, textvariable=self.memory_var).grid(row=0, column=1, padx=10, pady=10)

        tk.Label(root, text="Número de Procesos:").grid(row=1, column=0, padx=10, pady=10)
        tk.Entry(root, textvariable=self.process_var).grid(row=1, column=1, padx=10, pady=10)

        # Botón de inicio
        tk.Button(root, text="Iniciar Simulación", command=self.start_simulation).grid(row=2, column=0, columnspan=2, pady=20)

        # Área de texto para mostrar los resultados
        self.output_text = tk.Text(root, height=20, width=50)
        self.output_text.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

    def start_simulation(self):
        try:
            memory = self.memory_var.get()
            processes = self.process_var.get()

            if memory <= 0 or processes <= 0:
                raise ValueError("La memoria y el número de procesos deben ser mayores que cero.")

            # Inicializa la simulación
            app = segmentator.RunSegmentation(memory)
            for i in range(processes):
                inserted = app.start_new_process(i + 101)
                if inserted:
                    self.output_text.insert(
                        tk.END,
                        f"PID {inserted[0]}\n"
                        f"Memoria: {app.memory} Bytes\n"
                        f"SEGMENTO: {hex(app.segmentation_table.segments[-1][3].segments[0].base)} - {hex(app.segmentation_table.segments[-1][3].segments[0].limit)} ({app.segmentation_table.segments[0][3].memory} Bytes)\n"
                        f"DIRECCION BASE ACTUAL: {app.get_current_base_address()}\n"
                        f"MEMORIA USADA: {app.segmentation_table.get_memory_usage()} Bytes\n"
                        f"{app.memory - app.segmentation_table.get_memory_usage()} Bytes disponibles\n\n"
                    )
                self.root.update()
                self.root.after(2000)  # Simula una espera de 2 segundos

            while len(app.process_queue) > 0:
                self.output_text.insert(tk.END, f"Revisando cola ... (en cola: {len(app.process_queue)})\n")
                app.check_queue()
                self.root.update()
                self.root.after(2000)

            self.output_text.insert(tk.END, "\nVerificando existencia de procesos pendientes de terminar...\n")
            while app.segmentation_table.exists_processes():
                app.check_queue()
                self.root.update()
                self.root.after(2000)

            self.output_text.insert(tk.END, "Simulación terminada\n")

        except ValueError as e:
            messagebox.showerror("Error", str(e))
        except Exception as e:
            messagebox.showerror("Error inesperado", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    app = MemorySimulatorApp(root)
    root.mainloop()
