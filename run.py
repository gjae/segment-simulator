
import tkinter as tk
from tkinter import messagebox
import clases as segmentator

class MemorySimulatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulador de Segmentación de Memoria")

        # Variables de la interfaz

        self.memory_var = tk.StringVar()
        self.process_var = tk.StringVar()


        # Etiquetas y campos de entrada
        tk.Label(root, text="Memoria Total (Bytes):").grid(row=0, column=0, padx=10, pady=10)
        tk.Entry(root, textvariable=self.memory_var).grid(row=0, column=1, padx=10, pady=10)

        tk.Label(root, text="Número de Procesos:").grid(row=1, column=0, padx=10, pady=10)
        tk.Entry(root, textvariable=self.process_var).grid(row=1, column=1, padx=10, pady=10)

        # Botón de inicio
        tk.Button(root, text="Iniciar Simulación", command=self.start_simulation).grid(row=2, column=0, columnspan=2, pady=20)

        # Área de texto para mostrar los resultados

        self.output_text = tk.Text(root, height=20, width=80)
        self.output_text.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

        # Definir las etiquetas de color
        self.output_text.tag_configure("info", foreground="blue")
        self.output_text.tag_configure("error", foreground="red")
        self.output_text.tag_configure("warning", foreground="orange")
        self.output_text.tag_configure("segment", foreground="green")
        self.output_text.tag_configure("queue", foreground="purple")
        self.output_text.tag_configure("finished", foreground="gray")
        self.output_text.tag_configure("process", foreground="black")

    def display_processes(self, segmentation_table):
        # Muestra el estado actual de los procesos en la tabla de segmentos
        self.output_text.insert(tk.END, "\nEstado Actual de los Procesos:\n", "info")
        self.output_text.insert(tk.END, "PID | Base | Limite | Uso | Estado\n", "info")
        for segment in segmentation_table.segments:
            pid, base, limit, process, usage, status = segment
            status_str = "Ocupado" if status == segmentator.StatusEnum.FULL else "Libre"
            tag = "segment" if status == segmentator.StatusEnum.FULL else "finished"
            self.output_text.insert(tk.END, f"{pid} | {hex(base)} | {hex(limit)} | {usage} Bytes | {status_str}\n", tag)
        self.output_text.insert(tk.END, "\n")

    def start_simulation(self):
        try:
            # Lee y valida los valores de entrada
            memory = int(self.memory_var.get())
            processes = int(self.process_var.get())

            if memory <= 0 or processes <= 0:
                raise ValueError("La memoria y el número de procesos deben ser mayores que cero.")
            
            # Inicializa la simulación
            app = segmentator.RunSegmentation(memory)
            process_queue = []  # Cola para procesos que no se pueden insertar de inmediato

            # Genera y trata de insertar los procesos
            for i in range(processes):
                pid = i + 101
                inserted = app.start_new_process(pid)
                if inserted:
                    self.output_text.insert(
                        tk.END,
                        f"Nuevo proceso insertado: PID {pid}, requiere: {inserted[2]} Bytes / Usado: {app.segmentation_table.get_memory_usage()} / Base: {hex(inserted[1])}\n",
                        "info"
                    )
                else:
                    process_queue.append(pid)  # Añadir a la cola si no se pudo insertar
                    self.output_text.insert(tk.END, f"Proceso {pid} en cola ... \n", "queue")

                self.root.update()
                self.root.after(1000)  # Espera 1 segundo

            # Mostrar el estado inicial de los procesos
            self.display_processes(app.segmentation_table)

            while len(process_queue) > 0 or app.segmentation_table.exists_processes():
                # Simula la recolección de basura
                self.output_text.insert(tk.END, "Ejecutando recolector de basura...\n", "warning")
                finished_processes = app.segmentation_table.check_process()
                self.output_text.insert(tk.END, f"Recolector de basura ha liberado {len(finished_processes)} procesos\n", "warning")
                
                # Mostrar el estado después de la recolección de basura
                self.display_processes(app.segmentation_table)
                
                self.root.update()
                self.root.after(1000)  # Espera 1 segundo

                # Reintenta insertar los procesos en cola
                if process_queue:
                    pid = process_queue.pop(0)
                    inserted = app.start_new_process(pid)
                    if inserted:
                        self.output_text.insert(
                            tk.END,
                            f"PID: {pid} proceso sacado de la cola y en ejecución\n"
                            f"Memoria Total usada: {inserted[2]} Bytes\n"
                            f"SEGMENTO :  {hex(inserted[1])} - {hex(inserted[1] + inserted[2] - 1)}\n"
                            f"DIRECCION BASE ACTUAL: {app.get_current_base_address()}\n"
                            f"MEMORIA USADA: {app.segmentation_table.get_memory_usage()} Bytes\n"
                            f"{app.memory - app.segmentation_table.get_memory_usage()} Bytes disponibles\n\n",
                            "info"
                        )
                    else:
                        process_queue.insert(0, pid)  # Reinsertar en la cola si aún no se puede insertar

                # Mostrar el estado después de intentar insertar procesos
                self.display_processes(app.segmentation_table)

                self.root.update()
                self.root.after(1000)  # Espera 1 segundo

            self.output_text.insert(tk.END, "Simulación terminada\n", "info")

        except ValueError as e:
            self.output_text.insert(tk.END, f"Error de Entrada: {str(e)}\n", "error")
        except Exception as e:
            self.output_text.insert(tk.END, f"Error Inesperado: {str(e)}\n", "error")

if __name__ == "__main__":
    root = tk.Tk()  # Crea la ventana principal de la aplicación
    app = MemorySimulatorApp(root)  # Crea una instancia de la aplicación
    root.mainloop()  # Inicia el bucle principal de la interfaz gráfica
