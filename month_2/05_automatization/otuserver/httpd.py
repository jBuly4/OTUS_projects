import logging
from concurrent.futures import ThreadPoolExecutor

from console_parser import add_argument_parser
from services import request_processor
from simple_server import SimpleHTTPServer


def submit_to_executor(workers, request_bytes):
    """Submit future task"""
    executor = ThreadPoolExecutor(max_workers=workers)
    return executor.submit(request_processor, request_bytes)


if __name__ == '__main__':
    logging.basicConfig(
            format='[%(asctime)s] %(levelname).1s %(message)s',
            level=logging.INFO, datefmt='%Y.%m.%d %H:%M:%S'
    )

    server_opts = add_argument_parser()

    try:
        otuserver = SimpleHTTPServer(
                server_opts.doc_root,
                server_opts.address,
                int(server_opts.port),
                server_opts.workers,
        )
        otuserver.start_new_request_parsing = submit_to_executor
        otuserver.serve_forever()
    except Exception:
        logging.exception("Huston, we got a problem!")
        otuserver.close_server_socket()
    except KeyboardInterrupt:
        logging.exception("Stopping OTUServer, good bye!")
        otuserver.close_server_socket()
