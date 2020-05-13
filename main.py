import parser
import scanner
import argparse


def main():
    p = argparse.ArgumentParser(
        description='Compiler or RSRCC that targets the RSRC architecture'
    )
    p.add_argument("source", type=str, help="source file")
    args = p.parse_args()
    try:
        with open(args.source, "rb") as f:
            _prolog()
            _init(f)
            parser._program(f)
            _epilog()
    except IOError as e:
        print(e)
        print("Couldn't open file {}".format(args.source))


def _init(f):
    scanner._nchar = f.read(1).decode("utf-8")


def _prolog():
    print(".org 4096")


def _epilog():
    print("END")


if __name__ == "__main__":
    main()
