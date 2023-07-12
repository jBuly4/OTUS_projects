import argparse


def add_argument_parser():
    """Get arguments from command line using argparse."""
    parser = argparse.ArgumentParser(description="<--------------------->\n"
                                                 "<----- OTUServer ----->\n"
                                                 "<--------------------->")
    parser.add_argument(
            "-a",
            dest="address",
            type=str,
            default="127.0.0.1",
            help="Set server address"
    )

    parser.add_argument(
            "-p",
            dest='port',
            type=int,
            default=80,
            help="Set server port"
    )

    parser.add_argument(
            "-w",
            dest="workers",
            type=int,
            default=20,
            help="Set number of workers for Server"
    )

    parser.add_argument(
            "-r",
            dest="doc_root",
            type=str,
            default="tests",
            help="Set document root directory"
    )

    return parser.parse_args()
