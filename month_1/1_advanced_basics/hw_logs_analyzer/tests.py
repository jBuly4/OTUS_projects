import logging
import tempfile
import unittest

from collections import defaultdict, namedtuple
from datetime import datetime
from gzip import GzipFile
from pathlib import Path
from re import compile
from unittest.mock import mock_open, patch

from log_analyzer import prepare_config, find_log_last, log_is_reported, read_log, parse_line, collect_info

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
    def test_ERROR_logging(self):
        default_config = {'key1': 'value1', 'key2': 'value2'}
        path_to_config = 'nonexistent_file.json'

        with self.assertRaises(FileNotFoundError):
            with self.assertLogs(level='ERROR') as logs:
                # Call the function with a nonexistent file path
                prepare_config(default_config, path_to_config)

                # Check that a ERROR message was logged with the expected content
                expected_log = f'ERROR:root:Config file not found: {path_to_config}'
                self.assertIn(expected_log, logs.output)

        # Check that the logs contained a ERROR message
        if len(logs.output) == 0:
            raise AssertionError('No ERROR message logged')

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
        with self.assertLogs(level='ERROR') as logs:
            with self.assertRaises(FileNotFoundError):  # to catch exceptions and then check logs outside of that
                # 'with' block
                result = find_log_last(str(self.log_dir), self.log_file_pattern)

                # The \nNoneType: None part in the error message is likely being appended by the logging.exception
                # call in the find_log_last function. The logging.exception call logs an error message along with the
                # traceback of the exception that was raised, which can result in the extra information being added
                # to the log message.

            expected_logs = [
                'ERROR:root:ERROR! Latest log was not found!',
            ]

            for log in expected_logs:
                self.assertIn(log, logs.output)

    def test_with_matching_logs(self):  # works
        with open(self.log_dir / 'nginx-access-ui.log-20220320.gz', 'w') as file:
            file.write('This is a test log')
        expected_log = (str(self.log_dir / 'nginx-access-ui.log-20220320.gz'), datetime(2022, 3, 20))

        actual_log = find_log_last(str(self.log_dir), self.log_file_pattern)

        self.assertEqual(str(actual_log.log_name), expected_log[0])
        self.assertEqual(actual_log.log_date, expected_log[1])

    def test_with_multiple_matching_logs(self):
        with open(self.log_dir / 'nginx-access-ui.log-20220320.gz', 'w') as file:
            file.write('This is a test log')
        with open(self.log_dir / 'nginx-access-ui.log-20220321.gz', 'w') as file:
            file.write('This is a test log')
        expected_log = (self.log_dir / 'nginx-access-ui.log-20220321.gz', datetime(2022, 3, 21))

        actual_log = find_log_last(str(self.log_dir), self.log_file_pattern)

        self.assertEqual(actual_log.log_name, expected_log[0])
        self.assertEqual(actual_log.log_date, expected_log[1])


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


class TestReadLog(unittest.TestCase):
    def setUp(self) -> None:
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b'line1\nline2\nline3')
            self.temp_file = Path(f.name)
        self.expected_output = [b'line1\n', b'line2\n', b'line3']  # because we don't decode in read_log

        with open(self.temp_file, 'rb') as f:
            contents = f.read()
            with GzipFile(mode='wb', filename=str(self.temp_file) + '.gz') as gz:
                gz.write(contents)

        self.temp_file_gz = Path(str(self.temp_file) + '.gz')

    def tearDown(self) -> None:
        self.temp_file.unlink()
        self.temp_file_gz.unlink()

    def test_read_log_uncompressed(self):
        output = [line for line in read_log(self.temp_file_gz)]
        self.assertEqual(output, self.expected_output)

    def test_read_log_compressed(self):
        output = [line for line in read_log(self.temp_file_gz)]
        self.assertEqual(output, self.expected_output)


class TestParseLine(unittest.TestCase):
    def test_parse_line(self):
        test_cases = [
            (
                '1.196.116.32 -  - [29/Jun/2017:03:50:22 +0300] "GET /api/v2/banner/25019354 HTTP/1.1" 200 927 "-" '
                '"Lynx/2.8.8dev.9 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/2.10.5" "-" "1498697422-2190034393-4708-9752759" '
                '"dc7161be3" 0.390\n',
                ('/api/v2/banner/25019354', 0.39),
            ),
            (
                b'1.99.174.176 3b81f63526fa8  - [29/Jun/2017:03:50:22 +0300] "GET '
                b'/api/1/photogenic_banners/list/?server_name=WIN7RB4 HTTP/1.1" 200 12 "-" "Python-urllib/2.7" "-" '
                b'"1498697422-32900793-4708-9752770" "-" 0.133\n',
                ('/api/1/photogenic_banners/list/?server_name=WIN7RB4', 0.133),
            ),
            (
                '1.169.137.128 -  - [29/Jun/2017:03:50:22 +0300] "GET /api/v2/banner/16852664 HTTP/1.1" 200 19415 "-" '
                '"Slotovod" "-" "1498697422-2118016444-4708-9752769" "712e90144abee9" 0.199\n',
                ('/api/v2/banner/16852664', 0.199),
            ),
        ]

        for line, expected_result in test_cases:
            with self.subTest(line=line, expected_result=expected_result):
                result = parse_line(line)
                self.assertEqual(tuple(result), expected_result)

class TestCollector(unittest.TestCase):
    def test_collector(self):
        test_collector = defaultdict(dict)
        expected_values = defaultdict(dict)
        expected_values['url1']['url_rt'] = 3.0
        expected_values['url1']['num_of_url'] = 5
        expected_values['url1']['url_rt_max'] = 0.6
        expected_values['url2']['url_rt'] = 1.4
        expected_values['url2']['num_of_url'] = 2
        expected_values['url2']['url_rt_max'] = 0.7

        test_data = {
            'url1': {
                'request': 0.6,
            },
            'url2': {
                'request': 0.7
            }
        }
        x = 5
        while x > 0:
            test_collector = collect_info(test_collector, 'url1', test_data['url1']['request'])
            if x < 3:
                test_collector = collect_info(test_collector, 'url2', test_data['url2']['request'])

            x -= 1

        self.assertEqual(test_collector, expected_values)


if __name__ == '__main__':
    unittest.main()
