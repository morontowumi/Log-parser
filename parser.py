"""Count failed logons from a file or the local mock API."""
import csv
import json
import sys
import requests
from pathlib import Path
import os
import time

def fetch(url):
    if not url.startswith(('http://127.0.0.1:', 'http://localhost:')):
        raise ValueError('Only a local mock API is allowed')#this is just for now

    token = os.getenv('MOCKAPITOKEN')
    headers = {'Authorization': f'Bearer {token}'} if token else {}
    events = []
    for page in range(1, 101):
        for attempt in range(3):
            try:
                response = requests.get(f"{url.rstrip('/')}/logs", params={'page': page},
                                        headers=headers, timeout=2)
                response.raise_for_status()
                data = response.json()
                if not isinstance(data, dict) or not isinstance(data.get('events'), list) or not isinstance(data.get('has_next'), bool):
                    raise ValueError('Invalid API response')
                if not all(isinstance(event, dict) for event in data['events']):
                    raise ValueError('Invalid API event')
                break
            except requests.HTTPError as error:
                status = error.response.status_code
                if status < 500 and status != 429:
                    raise RuntimeError(f'API returned HTTP {status}') from None
                if attempt == 2:
                    raise RuntimeError(f'API failed on page {page} after 3 attempts') from None
            except (requests.RequestException, ValueError):
                if attempt == 2:
                    raise RuntimeError(f'API failed on page {page} after 3 attempts') from None
            time.sleep(0.1)

        events.extend(data['events'])
        if not data['has_next']:
            return events
    raise RuntimeError('API exceeded 100 pages')
    
def count(events):
    results = {}
    for number, event in enumerate(events, 1):
        if str(event.get('EventID')) != '4625':
            continue
        user = event.get('Username')
        ip = event.get('SourceIP')
        if not isinstance(user, str) or not user.strip() or not isinstance(ip, str) or not ip.strip():
            print(f'Skipping malformed record {number}', file=sys.stderr)
            continue
        key = (user, ip)
        results[key] = results.get(key, 0) + 1
    return results


def readlog(path):
    events = []
    with open(path) as file:
        for number, line in enumerate(file, 1):
            fields = {}
            for part in line.split():
                if '=' in part:
                    key, value = part.split('=', 1)
                    fields[key] = value
            if fields.get('EventID') == '4625' and (not fields.get('Username') or not fields.get('SourceIP')):
                print(f'Malformed failed logon on line {number}', file=sys.stderr)
            events.append(fields)
    return events


def save(results, csvpath, jsonpath):
    rows = [dict(Username=user, Source_IP=ip, Attempts=total)
            for (user, ip), total in sorted(results.items())]
    with open(csvpath, 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['Username', 'Source_IP', 'Attempts'])
        writer.writeheader()
        writer.writerows(rows)
    with open(jsonpath, 'w') as file:
        json.dump(rows, file, indent=2)
        file.write('\n')


def main():
    # Examples:
    # python parser.py file samples/failed_logons.txt out.csv out.json
    # python parser.py api http://127.0.0.1:8000 out.csv out.json
    if len(sys.argv) != 5 or sys.argv[1] not in ('file', 'api'):
        print('Usage: python parser.py file|api INPUT out.csv out.json', file=sys.stderr)
        return 1

    mode, source, csvpath, jsonpath = sys.argv[1:]
    paths = [Path(csvpath).resolve(), Path(jsonpath).resolve()]
    if mode == 'file':
        paths.append(Path(source).resolve())
    if len(set(paths)) != len(paths):
        print('Error: input and output must use different paths', file=sys.stderr)
        return 1

    try:
        events = readlog(source) if mode == 'file' else fetch(source)
        results = count(events)
        save(results, csvpath, jsonpath)
        print(f'Saved {sum(results.values())} failed logons from {len(results)} account/IP groups')
        return 0
    except (OSError, UnicodeError, ValueError, RuntimeError) as error:
        print(f'Error: {error}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
