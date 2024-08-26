import argparse
import sys


def start(args):
    print(args.memory)


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