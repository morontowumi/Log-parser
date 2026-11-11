# Failed Logon Security Utility

## Purpose

This Python utility analyses failed login attempts from a local log file or a mock API. It groups failed logins by username and source IP address and generates CSV and JSON reports.

It also handles malformed log records, API timeouts, pagination and retries.

## Files

- `parser.py` – Retrieves and analyses failed login records.
- `mockapi.py` – Simulates an API that provides login records.
- `test_parser.py` – Contains automated tests.
- `samples/failed_logons.txt` – Sample login records.

## Installation

Install the required packages: pytest and requests
python -m pip install requests
python -m pip install pytest

## Usage

**1. Analyse a local log file**

```bash
python parser.py file samples/failed_logons.txt report.csv report.json
```

**2. Analyse logs from the mock API**

Start the mock API:

```bash
python mockapi.py
```

Open another terminal and run:

```bash
python parser.py api http://127.0.0.1:8000 report.csv report.json
```

**3. Run automated tests**

```bash
python -m pytest -v
```

## Output

The utility generates two reports:

- `report.csv` – Failed login counts in CSV format.
- `report.json` – Failed login counts in JSON format.

Both reports show the username, source IP address and number of failed login attempts.