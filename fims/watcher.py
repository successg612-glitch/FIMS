import time

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


class ChangeHandler(FileSystemEventHandler):
    def __init__(self, on_change_callback):
        self.on_change_callback = on_change_callback

    def on_created(self, event):
        if not event.is_directory:
            self.on_change_callback(event.src_path)

    def on_modified(self, event):
        if not event.is_directory:
            self.on_change_callback(event.src_path)

    def on_deleted(self, event):
        if not event.is_directory:
            self.on_change_callback(event.src_path)

    def on_moved(self, event):
        if not event.is_directory:
            # A rename/move is a disappearance at src_path and an appearance
            # at dest_path — report both so the old name isn't silently dropped.
            self.on_change_callback(event.src_path)
            self.on_change_callback(event.dest_path)


def start_watching(path, on_change_callback, on_tick=None, tick_interval=1):
    """Watch `path` with Watchdog's Observer + FileSystemEventHandler and
    invoke on_change_callback(filepath) for created/modified/deleted/moved events.
    If given, on_tick() is called once per tick_interval seconds so the caller
    can flush time-based state (e.g. resolving delete+recreate as a replace)."""
    handler = ChangeHandler(on_change_callback)
    observer = Observer()
    observer.schedule(handler, path, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(tick_interval)
            if on_tick:
                on_tick()
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
