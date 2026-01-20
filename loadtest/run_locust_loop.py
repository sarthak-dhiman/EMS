import subprocess
import time
import csv
import os

# Strategy: run Locust headless for a fixed duration and read CSV stats to determine total requests.
# Start target_requests at 1200, increase by 200 until we observe failures or cannot reach target within run.

DOCKER_COMPOSE = os.getenv('DOCKER_COMPOSE_CMD', 'docker compose')
LOCUST_FILE = '/app/loadtest/locustfile.py'
HOST = 'http://backend:8000'
RUN_TIME = '00:00:30'  # 30 seconds per run
CSV_PREFIX = '/tmp/locust_run'


def run_locust(users, spawn_rate, run_id):
    csv_base = f"{CSV_PREFIX}_{run_id}"
    cmd = [
        *DOCKER_COMPOSE.split(),
        'run', '--rm', 'locust',
        'locust', '-f', LOCUST_FILE,
        '--headless',
        '-u', str(users),
        '-r', str(spawn_rate),
        '--run-time', RUN_TIME,
        '--host', HOST,
        '--csv', csv_base,
        '--only-summary'
    ]
    print('Running:', ' '.join(cmd))
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    print(proc.stdout)
    return csv_base, proc.returncode


def parse_csv_stats(csv_base):
    stats_file = f"{csv_base}_stats.csv"
    if not os.path.exists(stats_file):
        return None
    total_reqs = 0
    total_failures = 0
    with open(stats_file, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get('Name') == 'Total':
                try:
                    total_reqs = int(row.get('Requests', 0))
                    total_failures = int(row.get('Failures', 0))
                except Exception:
                    pass
                break
    return total_reqs, total_failures


if __name__ == '__main__':
    target = 1200
    increment = 200
    run_id = 0
    max_users = 2000

    while True:
        run_id += 1
        # crude user estimate: aim users = min(max_users, target // 5)
        users = min(max_users, max(10, target // 5))
        spawn_rate = max(1, users // 2)
        csv_base, rc = run_locust(users, spawn_rate, run_id)
        # allow small delay for CSV to be flushed
        time.sleep(2)
        stats = parse_csv_stats(csv_base)
        if stats is None:
            print('No CSV stats found; stopping.')
            break
        total_reqs, failures = stats
        print(f"Run {run_id}: target={target} users={users} total_requests={total_reqs} failures={failures}")

        # cleanup csv files
        for suffix in ['_stats.csv', '_stats_history.csv', '_failures.csv']:
            fn = f"{csv_base}{suffix}"
            try:
                if os.path.exists(fn):
                    os.remove(fn)
            except Exception:
                pass

        if failures > 0:
            print('Failures observed; stopping loop.')
            break

        if total_reqs < target:
            print(f"Did not reach target {target} (only {total_reqs}). Stopping.")
            break

        # success -> increase target and continue
        target += increment
        print(f"Target reached. Increasing target to {target} and continuing...")

*** End Patch