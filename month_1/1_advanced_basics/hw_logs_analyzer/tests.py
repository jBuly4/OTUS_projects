import logging
import unittest
from unittest.mock import mock_open, patch

from log_analyzer import prepare_config

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

    # TODO: this tests doesn't work correctly, check with mentor
    def test_info_logging(self):
        default_config = {'key1': 'value1', 'key2': 'value2'}
        path_to_config = 'valid_file.json'
        file_contents = '{"key2": "new_value2", "key3": "value3"}'

        with patch('builtins.open', mock_open(read_data=file_contents)) as mock_file:
            # Check default config
            actual_config = prepare_config(default_config)

            # Call the function with a valid file path
            actual_config_2 = prepare_config(default_config, path_to_config)

            # Check that the file was opened with the correct path
            mock_file.assert_called_once_with(path_to_config)

        # Check that the expected log messages were generated
        with self.assertLogs(level='INFO') as logs:
            expected_logs = [
                f'INFO:root:Used default config',
                f'INFO:root:Loaded config from file: {path_to_config}',
            ]

            for log in expected_logs:
                self.assertIn(log, logs.output)


if __name__ == '__main__':
    unittest.main()
