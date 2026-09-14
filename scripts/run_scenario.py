"""Функциональные тесты запущенного контейнера по config/scenario.json."""
import json
import sys

import requests


def main() -> int:
    with open('config/scenario.json') as f:
        scenario = json.load(f)

    base_url = 'http://localhost:5000'
    failed = 0

    for tc in scenario['test_cases']:
        url = base_url + tc['endpoint']
        method = tc['method']
        payload = tc.get('payload')

        if method == 'GET':
            r = requests.get(url)
        else:
            r = requests.post(url, json=payload)

        print(f"[{tc['name']}] status={r.status_code}", flush=True)

        if r.status_code != tc['expected_status']:
            print(f"  FAIL: expected {tc['expected_status']}, got {r.status_code}", flush=True)
            failed += 1
            continue

        if 'expected_body_contains' in tc:
            body = r.json()
            for key, value in tc['expected_body_contains'].items():
                if body.get(key) != value:
                    print(f"  FAIL: {key}={body.get(key)} != {value}", flush=True)
                    failed += 1

    if failed:
        print(f"\n{failed} test(s) failed", flush=True)
        return 1

    print("\nAll functional tests passed", flush=True)
    return 0


if __name__ == '__main__':
    sys.exit(main())