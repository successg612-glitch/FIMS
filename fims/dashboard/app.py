import atexit
import io
import os
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone

from flask import Flask, redirect, render_template, request, send_file, url_for

from fims.alerts import read_alerts, reset_alerts
from fims.config import load_watch_path, save_watch_path
from fims.export import alerts_to_csv_bytes, alerts_to_pdf_bytes
from fims.hashing import build_baseline

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BASELINE_CSV_PATH = os.path.join(BASE_DIR, "data", "baseline.csv")

app = Flask(__name__)

CHANGE_TYPES = ("created", "modified", "replaced", "deleted")

_watcher_process = None


def start_watcher(path):
    global _watcher_process
    stop_watcher()
    _watcher_process = subprocess.Popen(
        [sys.executable, "main.py", "watch", path],
        cwd=BASE_DIR,
    )


def stop_watcher():
    global _watcher_process
    if _watcher_process and _watcher_process.poll() is None:
        _watcher_process.terminate()
        try:
            _watcher_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            _watcher_process.kill()
    _watcher_process = None


def is_watching():
    return _watcher_process is not None and _watcher_process.poll() is None


atexit.register(stop_watcher)

_configured_path = load_watch_path()
if _configured_path and os.path.isdir(_configured_path):
    start_watcher(_configured_path)


def get_alerts():
    return read_alerts()


def build_state():
    alerts = get_alerts()
    counts = Counter(a.get("change_type", "unknown") for a in alerts)
    summary = [{"type": t, "count": counts.get(t, 0)} for t in CHANGE_TYPES]
    return {
        "alerts": list(reversed(alerts)),
        "total": len(alerts),
        "summary": summary,
        "current_path": load_watch_path() or "",
        "watching": is_watching(),
    }


@app.route("/")
def index():
    state = build_state()
    return render_template("index.html", error=request.args.get("error"), **state)


@app.route("/api/state")
def api_state():
    return build_state()


@app.route("/export/csv")
def export_csv():
    alerts = list(reversed(get_alerts()))
    data = alerts_to_csv_bytes(alerts)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    return send_file(
        io.BytesIO(data),
        mimetype="text/csv",
        as_attachment=True,
        download_name=f"fims_alerts_{stamp}.csv",
    )


@app.route("/export/pdf")
def export_pdf():
    alerts = list(reversed(get_alerts()))
    data = alerts_to_pdf_bytes(alerts)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    return send_file(
        io.BytesIO(data),
        mimetype="application/pdf",
        as_attachment=True,
        download_name=f"fims_alerts_{stamp}.pdf",
    )


@app.route("/configure", methods=["POST"])
def configure():
    path = request.form.get("path", "").strip()
    if not path or not os.path.isdir(path):
        return redirect(url_for("index", error="That path doesn't exist or isn't a directory."), code=303)

    build_baseline(path, BASELINE_CSV_PATH)
    save_watch_path(path)
    reset_alerts()
    start_watcher(path)
    return redirect(url_for("index"), code=303)


if __name__ == "__main__":
    app.run(debug=True)
