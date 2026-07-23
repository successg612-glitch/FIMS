import csv
import hashlib
import os
from datetime import datetime, timezone


def compute_sha256(filepath, chunk_size=65536):
    sha256 = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


def rehash_file(filepath):
    return compute_sha256(filepath)


def build_baseline(root_dir, csv_path):
    count = 0
    os.makedirs(os.path.dirname(csv_path) or ".", exist_ok=True)
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["filepath", "sha256_hash", "last_checked"])
        for dirpath, _dirnames, filenames in os.walk(root_dir):
            for name in filenames:
                filepath = os.path.join(dirpath, name)
                file_hash = compute_sha256(filepath)
                timestamp = datetime.now(timezone.utc).isoformat()
                writer.writerow([filepath, file_hash, timestamp])
                count += 1
    return count


def load_baseline(csv_path):
    baseline = {}
    with open(csv_path, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            baseline[row["filepath"]] = row["sha256_hash"]
    return baseline
