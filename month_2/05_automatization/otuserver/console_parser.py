import argparse


def add_argument_parser():
    parser = argparse.ArgumentParser(description="<--------------------->\n"
                                                 "<----- OTUServer ----->\n"
                                                 "<--------------------->")
    parser.add_argument(
            "-a",
            dest="address",
            default="127.0.0.1",
            help="Set server address"
    )

    parser.add_argument(
            "-p",
            dest='port',
            default=8080,
            help="Set server port"
    )

    parser.add_argument(
            "-w",
            dest="workers",
            default=10,
            help="Set number of workers for Server"
    )

    parser.add_argument(
            "-r",
            dest="doc_root",
            default="tests",
            help="Set document root directory"
    )

    return parser.parse_args()
