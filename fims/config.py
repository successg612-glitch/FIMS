import os

CONFIG_PATH = "data/config.txt"


def load_watch_path(config_path=CONFIG_PATH):
    if not os.path.exists(config_path):
        return None
    with open(config_path, "r", encoding="utf-8") as f:
        path = f.read().strip()
    return path or None


def save_watch_path(path, config_path=CONFIG_PATH):
    os.makedirs(os.path.dirname(config_path) or ".", exist_ok=True)
    with open(config_path, "w", encoding="utf-8") as f:
        f.write(path)
