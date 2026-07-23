import os
import sys
import time

from fims.alerts import log_alert
from fims.comparator import compare
from fims.hashing import build_baseline, load_baseline, rehash_file
from fims.watcher import start_watching

DEFAULT_CSV_PATH = "data/baseline.csv"

# How long to hold a deletion as "pending" waiting for a same-path recreation
# before treating it as a confirmed delete rather than a replace.
REPLACE_WINDOW_SECONDS = 0.75


def handle_change(baseline, pending_deletions, filepath):
    # A file reappearing shortly after being deleted is a replacement,
    # regardless of what compare() would otherwise classify it as.
    if filepath in pending_deletions and os.path.exists(filepath):
        pending_deletions.pop(filepath)
        log_alert(filepath, "replaced")
        print(f"[ALERT] replaced: {filepath}")
        baseline[filepath] = rehash_file(filepath)
        return

    change_type = compare(baseline, filepath)
    if not change_type:
        return

    if change_type == "deleted":
        # Defer logging: wait to see if a recreation arrives within the window.
        pending_deletions[filepath] = time.time()
        return

    log_alert(filepath, change_type)
    print(f"[ALERT] {change_type}: {filepath}")
    baseline[filepath] = rehash_file(filepath)


def flush_stale_deletions(baseline, pending_deletions):
    now = time.time()
    stale = [fp for fp, ts in pending_deletions.items() if now - ts >= REPLACE_WINDOW_SECONDS]
    for filepath in stale:
        pending_deletions.pop(filepath)
        log_alert(filepath, "deleted")
        print(f"[ALERT] deleted: {filepath}")
        baseline.pop(filepath, None)


def main():
    if len(sys.argv) < 3:
        print("Usage: python main.py baseline <directory>")
        print("       python main.py watch <directory>")
        sys.exit(1)

    command, root_dir = sys.argv[1], sys.argv[2]

    if command == "baseline":
        count = build_baseline(root_dir, DEFAULT_CSV_PATH)
        print(f"Baseline built: {count} file(s) hashed -> {DEFAULT_CSV_PATH}")
    elif command == "watch":
        baseline = load_baseline(DEFAULT_CSV_PATH)
        pending_deletions = {}
        print(f"Watching {root_dir} for changes... (Ctrl+C to stop)")
        start_watching(
            root_dir,
            lambda filepath: handle_change(baseline, pending_deletions, filepath),
            on_tick=lambda: flush_stale_deletions(baseline, pending_deletions),
            tick_interval=0.25,
        )
    else:
        print("Unknown command:", command)
        sys.exit(1)


if __name__ == "__main__":
    main()
