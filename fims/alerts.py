import csv
import os
from datetime import datetime, timezone

ALERTS_CSV_PATH = "data/alerts.csv"
ALERTS_HEADER = ["filepath", "change_type", "timestamp"]


def _has_valid_header(csv_path):
    with open(csv_path, "r", newline="", encoding="utf-8") as f:
        first_line = f.readline()
    return first_line.strip("\r\n").split(",") == ALERTS_HEADER


def log_alert(filepath, change_type, csv_path=ALERTS_CSV_PATH):
    os.makedirs(os.path.dirname(csv_path) or ".", exist_ok=True)
    file_exists = os.path.exists(csv_path)

    # A pre-existing file with the wrong (e.g. legacy) header would otherwise
    # be appended to forever, leaving every row unreadable by column name.
    if file_exists and os.path.getsize(csv_path) > 0 and not _has_valid_header(csv_path):
        stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        os.replace(csv_path, f"{csv_path}.bad-{stamp}")
        file_exists = False

    with open(csv_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(ALERTS_HEADER)
        writer.writerow([filepath, change_type, datetime.now(timezone.utc).isoformat()])


def read_alerts(csv_path=ALERTS_CSV_PATH):
    if not os.path.exists(csv_path):
        return []
    with open(csv_path, "r", newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def reset_alerts(csv_path=ALERTS_CSV_PATH):
    if os.path.exists(csv_path):
        os.remove(csv_path)
