from random import randint
from enum import IntEnum
from heapq import heapify
from typing import List, Optional, Tuple
from dataclasses import dataclass


class StatusEnum(IntEnum):
    FULL = 1
    FREE = 2


class Segment:

    def __init__(self, base_address, limit_address):
        """
        Esta simulacion, por cuestiones de simplicidadm, toma como premisa que cada direccion 
        equivale a 1 byte por lo que de la direccion 0x00001 a las direccion 0x00002 hay en total 2 bytes
        """
        self.base = base_address
        self.limit = limit_address

    @property
    def total_bytes(self) -> int:
        return self.base + self.limit

class Process:
    pid: int
    memory: int
    segments: List[Segment] = []


    def __init__(self, *, pid, memory, segments = []):
        self.pid = pid
        self.memory = memory
        self.segments = segments

    def total_bytes_usage(self):
        byte_counter = 0
        for segment in self.segments:
            byte_counter += segment.total_bytes

        return byte_counter
    
    def finished(self):
        return randint(1, 1500) % 2 == 0

class NewSegment:
    base: int
    limit: int
    bytes: int
    segment_table_index: int

    def __init__(self, *, base, limit, bytes, segment_table_index) -> None:
        self.base = base
        self.bytes = bytes
        self.limit = limit
        self.segment_table_index = segment_table_index

    @property
    def total_bytes(self) -> int:
        return self.base + self.limit

class SegmentTable:
    def __init__(self):
        """
        Cada segmento sera representado por una tupla con la estructura
        (PID, "base": base_address, "limit": limit_address, "status": 0 | 1, Process())
        el status representa si el segmento ha sido marcado como disponible para reasignar o ocupado

        la base de cada segmento deberia ser el siguiente al limite de su inmediatamente anterior
        por lo que permitira 2 cosas:
        1) las longitudes de cada segmento puede ser variable
        2) si dos segmentos son adyacentes, y ambos estan disponibles, la simulacion puede "unir" ambos segmentos para ahcer uno mas grande y
        alojar un proceso nuevo
        """
        self.segments: List[Process] = []

    def get_memory_usage(self) -> int:
        total = 0
        for segment in self.segments:
            if segment[5] == StatusEnum.FULL:
                continue
            total += segment[5].total_bytes_usage()

        return total

    def has_segments_available_for(self, memory_required) -> Optional[NewSegment]:
        for segment, idx in enumerate(self.segments):
            if segment[5] == StatusEnum.FULL:
                continue
            if segment[4] <= memory_required:
                _, base, limit, _, bytes_usage, _ = segment
                return NewSegment(base=base, limit=limit, segment_table_index=idx, bytes=bytes_usage)
            if len(self.segments) <= idx or self.segments[idx+1][5] == StatusEnum.FULL:
                return None
            
            # Si existen dos  segmentos adyacentes y la suma de sus longitudes en bytes
            # es igual o mayor a los bytes requeridos por el nuevo proceso
            # se "fusionan" los segmentos para tener uno mas grande y se limpian los procesos
            # de esos segmentos
            if (segment[idx][5] + self.segments[idx+1][5]) >= memory_required:
                base = segment[idx][1]
                limit = self.segments[idx+1][2]
                total_bytes = segment[idx][4] + self.segments[idx+1][4]
                del self.segments[idx+1]
                return NewSegment(base=base, limit=limit, segment_table_index=idx, bytes=total_bytes)
            
        return None
    
    def _format_process(self, process: Process) -> Tuple[int, int, int, Process, int, StatusEnum]:
        #0,1,2,3,4,5
        new_process =(
            process.pid, 
            process.segments[0].base, 
            process.segments[-1].limit, 
            process, 
            process.total_bytes_usage(),
            StatusEnum.FULL
        )

        return new_process


    def add(self, process: Process, base, limit):
        new_process = self._format_process(process)
        new_process[3].segments.append(Segment(base_address=base, limit_address=limit))
        self.segments.append(new_process)
        return new_process
    
    def add_process(self, process: Process):
        """
        Agregar nuevo proceso.
        Al agregar un proceso primero se verifica si la tabla de segmentos esta vacia, en ese caso
        se agrega el primer segmento el cual tendra una direccion base 0x1 y su direccion limite sera 0x1 + el numero de bytes de memoria requerida para el nuevo proceso

        Recordar: por cuestiones de simplicidad , cada direccion de memoria es igual a 1 byte por lo que en base = 0x1 y limite = 0x2 hay en total
        2 bytes ocupados
        """
        if len(self.segments) == 0:
            process.segments.append(Segment(0x1, process.memory))
            new_process = self._format_process(process)
            self.segments.append(new_process)
            return new_process
        
        new_segment_index = self.has_segments_available_for(process.total_bytes_usage())
        if new_segment_index is None:
            return None
        
        process.segments.append(Segment(new_segment_index.base, new_segment_index.limit))
        new_process = self._format_process(process)
        self.segments[new_segment_index] = new_process

        return new_process

    def check_process(self):
        for segment, idx in enumerate(self.segments):
            process: Process = segment[3]
            if process.finished():
                self.segments[idx] = (
                    process.pid, 
                    process.segments[0].base, 
                    process.segments[-1].limit, 
                    process, 
                    process.total_bytes_usage(),
                    StatusEnum.FREE
                )


class RunSegmentation:
    segmentation_table: SegmentTable
    memory: int

    # Implementa una lista de  procesos, en caso de que la "memoria"
    # no sea  suficiente para ejecutar el nuevo proceso que ingresa 
    processes_list: List[Process]
    
    # Cuando no se tiene mas memoria para un proceso
    # se agrega a la cola. Esta lista tiene comportamiento FIFO
    process_queue: List[Process]

    def __init__(self, max_memory: int):
        self.memory = max_memory
        self.segmentation_table = SegmentTable()
        self.current_base_address = 0x0000001
        self.process_queue = []
        
    def get_current_base_address(self) -> str:
        return hex(self.current_base_address)

    def append_queue_process(self, process: Process, index = 0):
        self.process_queue.insert(index, process)

    def check_queue(self):
        if len(self.process_queue) == 0:
            return True
        
        deque = self.process_queue.pop()

        if self.segmentation_table.add_process(deque) is not None:
            self.check_queue()
        else:
            self.append_queue_process(deque, len(self.process_queue))
            return True
        
        return False

    def start_new_process(self, pid):
        memory_usage = randint(1, self.memory)
        process = Process(pid=pid, memory=memory_usage, segments=[])
        process_inserted = self.segmentation_table.add_process(process)
        if process_inserted is not None:
            self.current_base_address = process_inserted[2]
            return True

        self.check_queue()
        while (self.current_base_address + process.memory) <  self.segmentation_table.get_memory_usage():
            process.segments.append(Segment(base_address=self.current_base_address, limit_address=self.current_base_address + memory_usage))
            self.segmentation_table.add(
                process, 
                self.current_base_address, 
                self.current_base_address + process.memory
            )
            self.current_base_address = self.current_base_address + process.memory
            return True
        
        self.append_queue_process(process)

    def check_for_process_finished(self):
        self.segmentation_table.check_process()