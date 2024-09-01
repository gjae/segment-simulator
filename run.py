import argparse
from time import sleep
import clases as segmentator
from multiprocessing import Process, Value

app: segmentator.RunSegmentation

def start(args):

    app = segmentator.RunSegmentation(args.memory)
    app.start_new_process(101)
    print(app, app.memory, app.segmentation_table.segments[0][3].memory, app.get_current_base_address())

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

    start(parser.parse_args())


if __name__ == "__main__":
    _run_simulation()