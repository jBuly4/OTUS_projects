# User guide for log files parser.

## Usage: 
```bash
python log_analyzer.py [-h] [--config CONFIG]
```
## Description
```bash
options:
  -h, --help       show this help message and exit
  --config CONFIG  Add a path to configuration file. Otherwise default config will be used

```
## Limitations

* Limit of number of lines to parse is 100 000 (if you don't need it then comment 298 and 299 lines of code)
* Logs should be at './log/' folder.
* Report template should be at root folder with script.
* Report will be generated at './reports/' folder.

## Output
Report exists:
```bash
####----##########----#### 
####----LOGS_PARSER----#### 
####----##########----####
[2023.05.01 23:53:02] I Used default config
[2023.05.01 23:53:02] I Logs had already been reported!
```
Report doesn't exist:
```bash
####----##########----####
####----LOGS_PARSER----####
####----##########----####
[2023.05.02 00:03:44] I Used default config
[2023.05.02 00:03:44] I Log was not reported! Starting to generate report.
[2023.05.02 00:03:47] I Log is read and parsed. Fails count 4, number of lines 100001.
Starting to calculate stats.
[2023.05.02 00:03:47] I Stats are calculated.
[2023.05.02 00:03:47] I Loading template for report.
[2023.05.02 00:03:47] I Report generated. Fails percent is 0.0.
[2023.05.02 00:03:47] I Complete!
```