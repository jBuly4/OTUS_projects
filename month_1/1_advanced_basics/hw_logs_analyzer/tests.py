import logging
import unittest

from collections import namedtuple
from datetime import datetime
from pathlib import Path
from re import compile
from unittest.mock import mock_open, patch

from log_analyzer import prepare_config, find_log_last, log_is_reported

logging.basicConfig(
            format='[%(asctime)s] %(levelname).1s %(message)s',
            level=logging.INFO, datefmt='%Y.%m.%d %H:%M:%S'
    )


class TestPrepareConfig(unittest.TestCase):
    def test_no_path_given(self):
        # Test that the function returns the default configuration when no path is given
        default_config = {'key1': 'value1', 'key2': 'value2'}
        expected_config = default_config.copy()

        actual_config = prepare_config(default_config)

        self.assertEqual(actual_config, expected_config)

    def test_file_not_found(self):
        # Test that the function raises a FileNotFoundError when the given file path does not exist
        default_config = {'key1': 'value1', 'key2': 'value2'}
        path_to_config = 'nonexistent_file.json'

        with self.assertRaises(FileNotFoundError):
            prepare_config(default_config, path_to_config)

    def test_valid_file(self):
        # Test that the function returns the expected configuration when a valid file path is given
        default_config = {'key1': 'value1', 'key2': 'value2'}
        path_to_config = 'valid_file.json'
        file_contents = '{"key2": "new_value2", "key3": "value3"}'
        expected_config = {'key1': 'value1', 'key2': 'new_value2', 'key3': 'value3'}

        # Use mock_open and patch to simulate reading from a file
        with patch('builtins.open', mock_open(read_data=file_contents)) as mock_file:
            # Call the function with the path to the mock file
            actual_config = prepare_config(default_config, path_to_config)

            # Check that the file was opened with the correct path
            mock_file.assert_called_once_with(path_to_config)

        # Check that the returned config is the expected one
        self.assertEqual(actual_config, expected_config)


class TestLoggingPrepareConfig(unittest.TestCase):
    def test_warning_logging(self):
        default_config = {'key1': 'value1', 'key2': 'value2'}
        path_to_config = 'nonexistent_file.json'

        with self.assertRaises(FileNotFoundError):
            with self.assertLogs(level='WARNING') as logs:
                # Call the function with a nonexistent file path
                prepare_config(default_config, path_to_config)

                # Check that a warning message was logged with the expected content
                expected_log = f'WARNING:root:Config file not found: {path_to_config}'
                self.assertIn(expected_log, logs.output)

        # Check that the logs contained a warning message
        if len(logs.output) == 0:
            raise AssertionError('No warning message logged')

    def test_info_logging(self):
        default_config = {'key1': 'value1', 'key2': 'value2'}
        path_to_config = 'valid_file.json'
        file_contents = '{"key2": "new_value2", "key3": "value3"}'

        # Check that the expected log messages were generated
        with self.assertLogs(level='INFO') as logs:
            with patch('builtins.open', mock_open(read_data=file_contents)) as mock_file:  # started to work when I
                # moved this 'with' block inside 'with self.assertLogs'
                # Check default config
                actual_config = prepare_config(default_config)

                # Call the function with a valid file path
                actual_config_2 = prepare_config(default_config, path_to_config)

                # Check that the file was opened with the correct path
                mock_file.assert_called_once_with(path_to_config)

            expected_logs = [
                f'INFO:root:Used default config',
                f'INFO:root:Loaded config from file: {path_to_config}',
            ]

            for log in expected_logs:
                self.assertIn(log, logs.output)


class TestFindLogLast(unittest.TestCase):
    def setUp(self):  # https://docs.python.org/3/library/unittest.html#unittest.TestCase.setUp
        self.log_dir = Path('test_log_dir')
        self.log_dir.mkdir(exist_ok=True)
        self.not_dir = Path('test_log_dir/test.txt')
        self.not_dir.touch(exist_ok=True)
        self.log_file_pattern = compile(r'^nginx-access-ui\.log-(\d{8})(|\.gz)$')

    def tearDown(self):  # https://docs.python.org/3/library/unittest.html#unittest.TestCase.tearDown
        for file in self.log_dir.glob('*'):
            file.unlink()
        self.log_dir.rmdir()

    def test_not_a_dir(self):  # check with mentor why doesn't catch
        with self.assertRaises(NotADirectoryError):
            find_log_last(str(self.not_dir), self.log_file_pattern)

    def test_with_no_logs(self):
        with self.assertRaises(FileNotFoundError):
            find_log_last(str(self.log_dir), self.log_file_pattern)

    def test_with_non_matching_logs(self):
        with open(self.log_dir / 'test.log', 'w') as file:
            file.write('This is a test log')
        with self.assertRaises(FileNotFoundError):
            find_log_last(str(self.log_dir), self.log_file_pattern)

    def test_latest_log_not_found_logs(self):
        with self.assertLogs(level='WARNING') as logs:
            with self.assertRaises(FileNotFoundError):  # to catch exceptions and then check logs outside of that
                # 'with' block
                result = find_log_last(str(self.log_dir), self.log_file_pattern)

            expected_logs = [
                'WARNING:root:Warning! Latest log was not found!',
            ]

            for log in expected_logs:
                self.assertIn(log, logs.output)

    def test_with_matching_logs(self):  # works
        with open(self.log_dir / 'nginx-access-ui.log-20220320.gz', 'w') as file:
            file.write('This is a test log')
        expected_log = (str(self.log_dir / 'nginx-access-ui.log-20220320.gz'), datetime(2022, 3, 20))

        actual_log = find_log_last(str(self.log_dir), self.log_file_pattern)

        self.assertEqual(str(actual_log.logname), expected_log[0])
        self.assertEqual(actual_log.logdate, expected_log[1])

    def test_with_multiple_matching_logs(self):
        with open(self.log_dir / 'nginx-access-ui.log-20220320.gz', 'w') as file:
            file.write('This is a test log')
        with open(self.log_dir / 'nginx-access-ui.log-20220321.gz', 'w') as file:
            file.write('This is a test log')
        expected_log = (self.log_dir / 'nginx-access-ui.log-20220321.gz', datetime(2022, 3, 21))

        actual_log = find_log_last(str(self.log_dir), self.log_file_pattern)

        self.assertEqual(actual_log.logname, expected_log[0])
        self.assertEqual(actual_log.logdate, expected_log[1])

class TestLogIsReported(unittest.TestCase):
    def setUp(self):
        self.log_dir = Path('test_log_dir')
        self.log_dir.mkdir(exist_ok=True)
        self.log_file = self.log_dir / 'nginx-access-ui.log-20220321.gz'
        self.log_file.touch(exist_ok=True)
        self.report_dir = Path('test_report_dir')
        self.report_dir.mkdir(exist_ok=True)

    def tearDown(self):
        for file in self.log_dir.glob('*'):
            file.unlink()
        self.log_dir.rmdir()
        for file in self.report_dir.glob('*'):
            file.unlink()
        self.report_dir.rmdir()

    def test_log_is_reported(self):
        report_name = f"report-2022.03.21.html"
        report_file = self.report_dir / report_name
        report_file.touch(exist_ok=True)
        log_file = namedtuple('log_file', ['logname', 'logdate'])
        log_file.logname = self.log_file
        log_file.logdate = datetime(2022, 3, 21)

        self.assertTrue(log_is_reported(log_file, str(self.report_dir)))

    def test_log_is_not_reported(self):
        log_file = namedtuple('log_file', ['logname', 'logdate'])
        log_file.logname = self.log_file
        log_file.logdate = datetime(2022, 3, 21)

        self.assertFalse(log_is_reported(log_file, str(self.report_dir)))

    def test_report_dir_not_exist(self):
        log_file = namedtuple('log_file', ['logname', 'logdate'])
        log_file.logname = self.log_file
        log_file.logdate = datetime(2022, 3, 21)

        with self.assertRaises(NotADirectoryError):
            log_is_reported(log_file, "not_existing_dir")


if __name__ == '__main__':
    unittest.main()
