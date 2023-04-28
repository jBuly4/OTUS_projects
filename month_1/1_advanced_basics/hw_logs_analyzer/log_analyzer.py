#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import gzip
import json
import logging
import re
import sys

from collections import defaultdict, namedtuple
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import DefaultDict, Generator, NamedTuple, Pattern, Union

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
        logging.exception(f'Config file not found: {path_to_config}')
        raise FileNotFoundError("Config file not found")


def find_log_last(path_to_log_dir: str, file_pattern: Pattern) -> NamedTuple:
    """
    Find the latest log in the dir.
    :param path_to_log_dir: path to directory with logs.
    :param file_pattern: name pattern for log file to search.
    :return: named tuple with log name and log date fields.
    """
    path = Path(path_to_log_dir)
    if not path.is_dir():
        logging.error("LOG_DIR is not a directory path")
        raise NotADirectoryError("Path to LOG_DIR is not pointing to a directory")

    LastLog = namedtuple("LastLog", ["log_name", "log_date"])
    latest_log_date = datetime(1, 1, 1)  # start point for dates comparison
    file_latest = None

    date_format = "%Y%m%d"  # classmethod datetime.strptime(date_string, format)
    for file in path.iterdir():
        match = file_pattern.match(str(file).split("/")[1])  # file is a path: dir_name/file
        if match:
            curr_date = datetime.strptime(match.group(1), date_format)
            if curr_date > latest_log_date:
                latest_log_date = curr_date
                file_latest = file

    last_log = LastLog(
            log_name=file_latest,
            log_date=latest_log_date
    )

    if last_log.log_date == datetime(1, 1, 1):
        logging.error("ERROR! Latest log was not found!")
        raise FileNotFoundError("Latest log was not found!")

    return last_log  # then call of this function should be inside outter try/except block


def log_is_reported(log_file: NamedTuple, report_dir: str) -> bool:
    """
    Check that logfile had been reported or not.
    :param log_file: path to logfile
    :param report_dir: path to report directory
    :return: bool
    """
    report_name = f"report-{log_file.logdate.strftime('%Y.%m.%d')}.html"
    report_path = report_dir + "/" + report_name

    if not Path(report_dir).exists():
        logging.exception("Exception raised while checking log was reported or not!")
        raise NotADirectoryError("Something wrong with path while checking is log was reported.")

    logging.info("Log was not reported!")
    return Path(report_path).exists()


def read_log(log_file: Path) -> Generator[Union[str, bytes], None, None]:
    with gzip.open(log_file) if log_file.suffix == '.gz' else open(log_file) as lf_handler:
        for line in lf_handler:
            yield line


def parse_line(line: Union[str, bytes]) -> NamedTuple:
    url_pattern = re.compile(r'\"\w+\s(\S+)\s+HTTP')
    request_time_pattern = re.compile(r'\d+\.\d+$')
    URLandReq_time = namedtuple("URLandReq_time", ["url", "request_time", "fail"])
    fail = False

    if isinstance(line, bytes):
        line = line.decode("UTF-8")

    url = url_pattern.search(line)  # https://docs.python.org/3/library/re.html?highlight=re%20match#search-vs-match
    request_time = request_time_pattern.search(line)

    if not url or not request_time:
        fail = True

        url_and_req_time = URLandReq_time(
                url=None,
                request_time=None,
                fail=fail
        )  # remember that you have to create an instance of namedtuple.

        return url_and_req_time

    url_and_req_time = URLandReq_time(
            url=url.group(1),
            request_time=round(float(request_time.group()), 3),
            fail=fail
    )

    return url_and_req_time


def collect_info(collector: DefaultDict[str, dict], url: str,
                 url_req_time: float, url_num: int = 1) -> DefaultDict[str, dict]:
    """
    Function to collect all data from parsed log for future stat calculations
    :param collector: initialized dictionary from caller function
    :param url: URL
    :param url_req_time: request time for URL
    :param url_num: appearance number of URL
    :return: updated collector
    """
    url_rt = 'url_rt'
    url_rt_max = 'url_rt_max'
    num_of_url = 'num_of_url'
    total = 'total'
    total_url_rt = 'total_url_rt'

    if url_rt not in collector[url].keys():
        collector[url][url_rt] = round(0.00, 2)

    if num_of_url not in collector[url].keys():
        collector[url][num_of_url] = 0

    if url_rt_max not in collector.keys():
        collector[url][url_rt_max] = round(0.00, 2)

    if url_req_time > collector[url][url_rt_max]:
        collector[url][url_rt_max] = round(url_req_time, 2)

    if total_url_rt not in collector[total].keys():
        collector[total][total_url_rt] = round(0.00, 2)

    # if we use += round(url_req_time, 3) then on next iterations result would be 1,789999999 etc
    collector[url][url_rt] = round(collector[url][url_rt] + url_req_time, 3)
    collector[url][num_of_url] = round(collector[url][num_of_url] + url_num, 3)
    collector[total][total_url_rt] = round(collector[total][total_url_rt] + url_req_time, 3)

    return collector


def calculate_stats():
    pass


def generate_report(log_file: NamedTuple, actual_config: dict) -> None:
    # read_log line by line.
    # parse line and return metrics needed: url, request time, count=1
    # save metrics at memory in the dictionary:
    # memory[url] = {request_time: float, count: int}.
    # memory[url][request_time] += request_time;
    # memory[url][count] += count
    # sort memory by request_time in descending order
    # calculate statistics
    # create_report: take read_log, create file, add lines from memory using, up to report_size limit
    pass


def main(actual_config: dict, file_pattern: Pattern) -> None:
    actual_log_file = find_log_last(actual_config.get("LOG_DIR"), file_pattern)  # recommended that
    # this function returns namedtuple

    if not actual_log_file:
        logging.info("No logs to report")
        return

    if not log_is_reported(actual_log_file, actual_config.get("REPORT_DIR")):
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
    log_file_pattern: Pattern[str] = re.compile("^nginx-access-ui\.log-(\d{8})(|\.gz)$")  # group 1 is date,
    # group 2 is file extension
    config = prepare_config(DEFAULT_CONFIG, args.config)
    main(config, log_file_pattern)
