#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import json


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
    config = default_config.copy()

    if not path_to_config:
        return config

    try:
        with open(path_to_config) as conf_handler:
            new_config = json.load(conf_handler.read())
            config.update(new_config)

            return config
    except FileNotFoundError:
        return  # TODO: add monitoring here and above to inform that config is updated



def main():
    pass


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
    config = prepare_config(DEFAULT_CONFIG, args.config)
    main()
