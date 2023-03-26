#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import json
import logging
import re
import sys

from collections import namedtuple
from pathlib import Path
from typing import NamedTuple, Pattern

# log_format ui_short '$remote_addr  $remote_user $http_x_real_ip [$time_local] "$request" '
#                     '$status $body_bytes_sent "$http_referer" '
#                     '"$http_user_agent" "$http_x_forwarded_for" "$http_X_REQUEST_ID" "$http_X_RB_USER" '  
#                     '$request_time';

DEFAULT_CONFIG = {
    "REPORT_SIZE": 1000,
    "REPORT_DIR": "./reports",
    "LOG_DIR": "./log",
    "LOG_FILE": None,
}


def prepare_config(default_config: dict, path_to_config: str = None) -> dict:
    """
    Check new config file and return updated config.
    :param default_config: config with default values
    :param path_to_config: path to new config file
    :return: updated config
    """
    actual_config = default_config.copy()

    if not path_to_config:
        logging.info('Used default config')
        return actual_config

    try:
        with open(path_to_config) as conf_handler:
            new_config = json.load(conf_handler)  # no .read() needed because json.load expects fileobject
            actual_config.update(new_config)

            logging.info(f'Loaded config from file: {path_to_config}')

            return actual_config
    except FileNotFoundError:
        logging.warning(f'Config file not found: {path_to_config}')
        raise FileNotFoundError("Config file not found")


def find_log_last(path_to_log_dir: str, log_file_pattern: Pattern) -> namedtuple:
    path = Path(path_to_log_dir)
    if not path.is_dir():
        logging.warning("LOG_DIR is not a directory path")
        raise NotADirectoryError("Path to LOG_DIR is not pointing to a directory")
    latest_log = namedtuple("latest_log", ["logname", "logdate"])
    date_format = "%Y%m%d"
    for file in path.iterdir():
        if log_file_pattern.match(file):
            pass

    # TODO: finish that function then create tests for it



def log_is_reported(log_file: NamedTuple) -> bool:
    pass


def generate_report(log_file: NamedTuple, actual_config: dict) -> None:
    pass


def main(actual_config: dict, log_file_pattern: Pattern) -> None:
    actual_log_file = find_log_last(actual_config.get("LOG_DIR"), log_file_pattern)  # recommended that
    # this function returns namedtuple

    if not actual_log_file:
        logging.info("No logs to report")
        return

    if not log_is_reported(actual_log_file):
        generate_report(actual_log_file, actual_config)
        logging.info("Report generated!")
        return
    else:
        logging.info("Logs had already been reported!")
        return


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
            description="####----##########----####\n"
                        "####----LOGS_PARSER----####\n"
                        "####----##########----####"
    )
    parser.add_argument(
            "--config",
            dest="config",
            help="Add a path to configuration file. Otherwise default config will be used"
    )
    args = parser.parse_args()
    logging.basicConfig(
            format='[%(asctime)s] %(levelname).1s %(message)s',
            level=logging.INFO, datefmt='%Y.%m.%d %H:%M:%S'
    )
    log_file_pattern: Pattern[str] = re.compile("^nginx-access-ui\.log-\d{8}$|\.gz")
    config = prepare_config(DEFAULT_CONFIG, args.config)
    main(config, log_file_pattern)
