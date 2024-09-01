import argparse
from time import sleep
import clases as segmentator
from multiprocessing import Process, Value

app: segmentator.RunSegmentation

def start(args):

    app = segmentator.RunSegmentation(args.memory)
    for i in range(args.process):
        inserted = app.start_new_process(i+101)
        if inserted:
            print(
                f"PID {inserted[0]}\n",
                "Memoria", app.memory, "\n",
                "SEGMENTO : ", hex(app.segmentation_table.segments[-1][3].segments[0].base), " - ", hex(app.segmentation_table.segments[-1][3].segments[0].limit) , "(", app.segmentation_table.segments[0][3].memory, "Bytes )\n", 
                "DIRECCION BASE ACTUAL: ", app.get_current_base_address(), "\n", 
                "MEMORIA USADA: ", app.segmentation_table.get_memory_usage(), "Bytes \n",
                app.memory - app.segmentation_table.get_memory_usage(), "Bytes disponibles"
            )
        sleep(2)

    while len(app.process_queue) > 0:
        sleep(2)
        print(f"Revisando cola ... (en cola: {len(app.process_queue)})")
        app.check_queue()
    
    print("\nVerificando existencia de procesos pendientes de terminar ...")
    while app.segmentation_table.exists_processes():
        sleep(2)
        app.check_queue()
    
    print("Simulacion terminada")

    
def _run_simulation():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--memory",
        "-m",
        type=int,
        help=(
            "Indica el numero de bytes con el que se ejecutara la simulacion"
        )
    )

    parser.add_argument(
        "--process",
        "-p",
        type=int,
        required=False,
        default=3
    )
    start(parser.parse_args())


if __name__ == "__main__":
    _run_simulation()