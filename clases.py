from random import randint
from enum import IntEnum
from typing import List, Optional, Tuple


# Enumeración que define el estado de un segmento de memoria
class StatusEnum(IntEnum):
    FULL = 1  # El segmento está ocupado
    FREE = 2  # El segmento está libre

# Clase que representa un segmento de memoria
class Segment:
    def __init__(self, base_address, limit_address):

        self.base = base_address  # Dirección base del segmento
        self.limit = limit_address  # Dirección límite del segmento

    @property
    def total_bytes(self) -> int:
        return self.limit - self.base  # Calcula el tamaño total del segmento


# Clase que representa un proceso

class Process:
    pid: int
    memory: int
    segments: List[Segment] = []  # Lista de segmentos asociados al proceso

    def __init__(self, *, pid, memory, segments=[]):

        self.pid = pid  # Identificador del proceso
        self.memory = memory  # Cantidad de memoria que necesita el proceso
        self.segments = segments  # Segmentos que ocupa el proceso

    def total_bytes_usage(self):
        byte_counter = 0
        # Suma el tamaño total de todos los segmentos del proceso
        for segment in self.segments:
            byte_counter += segment.total_bytes
        return byte_counter
    
    def finished(self):
        # Simula si un proceso ha terminado de manera aleatoria
        return randint(1, 1500) % 2 == 0


# Clase que representa un nuevo segmento de memoria para agregar a la tabla de segmentos

class NewSegment:
    base: int
    limit: int
    bytes: int
    segment_table_index: int

    def __init__(self, *, base, limit, bytes, segment_table_index) -> None:
        self.base = base  # Dirección base del nuevo segmento
        self.bytes = bytes  # Tamaño del nuevo segmento
        self.limit = limit  # Dirección límite del nuevo segmento
        self.segment_table_index = segment_table_index  # Índice en la tabla de segmentos

    @property
    def total_bytes(self) -> int:
        return self.limit - self.base  # Calcula el tamaño total del segmento

# Clase que representa la tabla de segmentos de memoria
class SegmentTable:
    def __init__(self):
        self.segments: List[Tuple[int, int, int, Process, int, StatusEnum]] = []
        # Cada entrada en la lista de segmentos es una tupla que contiene:
        # (PID del proceso, dirección base, dirección límite, objeto Process, uso en bytes, estado del segmento)

    def list_segments(self):
        print(self.segments)  # Imprime la lista de segmentos (para depuración)

    def get_memory_usage(self) -> int:
        total = 0
        # Calcula el uso total de memoria sumando los tamaños de los segmentos ocupados
        for segment in self.segments:
            if segment[5] == StatusEnum.FREE:
                continue
            total += segment[4]
        return total

    def has_segments_available_for(self, memory_required) -> Optional[NewSegment]:
        # Verifica si hay segmentos disponibles que puedan alojar la memoria requerida
        for idx, segment in enumerate(self.segments):
            if segment[5] == StatusEnum.FULL:
                continue
            if segment[4] <= memory_required:
                # Segmento disponible que es lo suficientemente grande
                _, base, limit, _, bytes_usage, _ = segment
                return NewSegment(base=base, limit=limit, segment_table_index=idx, bytes=bytes_usage)
            

            # Verifica si los segmentos contiguos pueden ser combinados
            if len(self.segments) <= idx or self.segments[idx + 1][5] == StatusEnum.FULL:
                return None
            
            if (segment[4] + self.segments[idx + 1][4]) >= memory_required:
                # Combina dos segmentos contiguos
                base = segment[1]
                limit = self.segments[idx + 1][2]
                total_bytes = segment[4] + self.segments[idx + 1][4]
                del self.segments[idx + 1]  # Elimina el segundo segmento

                return NewSegment(base=base, limit=limit, segment_table_index=idx, bytes=total_bytes)
            
        return None
    
    def _format_process(self, process: Process) -> Tuple[int, int, int, Process, int, StatusEnum]:

        # Crea una tupla que representa un proceso en la tabla de segmentos

        new_process = (
            process.pid, 
            process.segments[0].base, 
            process.segments[-1].limit, 
            process, 
            process.total_bytes_usage(),
            StatusEnum.FULL
        )
        return new_process

    def exists_processes(self) -> bool:

        # Verifica si hay procesos en la tabla de segmentos

        for segment in self.segments:
            if segment[5] == StatusEnum.FULL:
                return True
        return False
    
    def add(self, process: Process, base, limit):
        # Agrega un proceso a la tabla de segmentos con un nuevo segmento
        process.segments.append(Segment(base_address=base, limit_address=limit))
        new_process = self._format_process(process)
        self.segments.append(new_process)
        return new_process
    
    def add_process(self, process: Process):

        # Intenta agregar un proceso a la tabla de segmentos

        if len(self.segments) == 0:
            # Si la tabla está vacía, agrega el proceso con el primer segmento
            process.segments.append(Segment(0x1, process.memory))
            new_process = self._format_process(process)
            self.segments.append(new_process)
            return new_process
        
        # Intenta encontrar un segmento adecuado para el proceso
        new_segment_index = self.has_segments_available_for(process.total_bytes_usage())
        if new_segment_index is None:
            return None
        
        process.segments.append(Segment(new_segment_index.base, new_segment_index.limit))
        new_process = self._format_process(process)
        self.segments[new_segment_index.segment_table_index] = new_process

        return new_process

    def check_process(self):
        # Verifica los procesos en la tabla y libera la memoria de los procesos que han terminado
        finisheds = set()
        for idx, segment in enumerate(self.segments):
            process: Process = segment[3]
            if process.finished():
                # Marca el segmento como libre si el proceso ha terminado
                self.segments[idx] = (
                    process.pid, 
                    process.segments[0].base, 
                    process.segments[-1].limit, 
                    process, 
                    process.total_bytes_usage(),
                    StatusEnum.FREE
                )
                finisheds.add(self.segments[idx])
                del self.segments[idx]

        free = sum(list(map(lambda x: x[4], finisheds)))
        processing = [i[0] for i in self.segments]
        print(f"Recolector de basura ha liberado: {free} Bytes ({len(finisheds)} procesos limpiados), en proceso: {processing}")
        return finisheds


# Clase que representa la simulación de segmentación de memoria

class RunSegmentation:
    segmentation_table: SegmentTable
    memory: int


    processes_list: List[Process]

    # Implementa una lista de procesos, en caso de que la "memoria"
    # no sea suficiente para ejecutar el nuevo proceso que ingresa.
    
    # Cuando no se tiene más memoria para un proceso,
    # se agrega a la cola. Esta lista tiene comportamiento FIFO.

    process_queue: List[Process]

    def __init__(self, max_memory: int):
        self.memory = max_memory  # Memoria total disponible
        self.segmentation_table = SegmentTable()  # Inicializa la tabla de segmentos
        self.current_base_address = 0  # Dirección base actual para asignar memoria
        self.process_queue = []  # Cola para procesos que no pueden ser insertados inmediatamente
        
    def get_current_base_address(self) -> str:
        return hex(self.current_base_address)  # Devuelve la dirección base actual en formato hexadecimal

    def append_queue_process(self, process: Process, index=0):

        self.process_queue.insert(index, process)  # Añade un proceso a la cola en una posición específica


    def check_queue(self):
        self.check_for_process_finished()  # Verifica si hay procesos terminados
        if len(self.process_queue) == 0:
            return True

        deque = self.process_queue.pop()  # Extrae el último proceso de la cola
        inserted = self.segmentation_table.add_process(deque)
        if inserted is not None:
            print(f"PID: {deque.pid} proceso sacado de la cola y en ejecución")
            print(
                f"PID {inserted[0]} (DESENCOLADO)\n",
                "Memoria", deque.memory, "\n",
                "SEGMENTO : ", hex(self.segmentation_table.segments[-1][3].segments[0].base), " - ", hex(self.segmentation_table.segments[-1][3].segments[0].limit), "(", self.segmentation_table.segments[0][3].memory, "Bytes)\n", 
                "DIRECCION BASE ACTUAL: ", self.get_current_base_address(), "\n", 
                "MEMORIA USADA: ", self.segmentation_table.get_memory_usage(), "Bytes \n",
                self.memory - self.segmentation_table.get_memory_usage(), "Bytes disponibles"
            )
            self.check_queue()  # Revisa la cola nuevamente
        else:
            self.append_queue_process(deque, len(self.process_queue))  # Reintenta añadir el proceso a la cola
            return True
        
        return False

    def start_new_process(self, pid):
        memory_usage = randint(1, self.memory)  # Asigna aleatoriamente el tamaño de memoria necesario
        process = Process(pid=pid, memory=memory_usage, segments=[])
        
        print(f"Nuevo proceso: {process.pid}, requiere: {memory_usage} Bytes / Usado: {self.segmentation_table.get_memory_usage()} / Base: {self.get_current_base_address()}")
        
        if (self.segmentation_table.get_memory_usage() + process.memory) <= self.memory:

            # Intenta insertar el proceso en la memoria
            print(f"Insertando proceso {process.pid}")

            inserted = self.segmentation_table.add(
                process, 
                self.current_base_address, 
                self.current_base_address + process.memory
            )
            self.current_base_address += process.memory + 1  # Actualiza la dirección base
            return inserted
        else:
            process_inserted = self.segmentation_table.add_process(process)
            if process_inserted is not None:

                self.current_base_address = process_inserted[2] + 1  # Actualiza la dirección base
                return process_inserted

            self.append_queue_process(process)  # Añade el proceso a la cola si no se pudo insertar
            print("Proceso en cola ... ")
            return None


    def check_for_process_finished(self):
        # Verifica y limpia los procesos que han terminado
        finished = self.segmentation_table.check_process()

        if len(finished) > 0:
            for removed in finished:
                print(f"PID {removed[0]}: proceso terminado")
