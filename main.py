import os
import re
import time

import requests
from watchdog.events import FileSystemEventHandler
from watchdog.observers.polling import PollingObserver

from config.app import TARGET_DIR, TARGET_FILE, WEBHOOK_URL

class MinecraftLogMonitor:
    def __init__(self, target_dir, target_file, webhook_url):
        self.target_dir = target_dir
        self.target_file = target_file
        self.webhook_url = webhook_url
        self.prev_logs = []
        self.log_position = 0

    def send_message(self, message: str) -> None:
        main_content = {"content": message}
        response = requests.post(self.webhook_url, json=main_content)
        response.raise_for_status()

    def message_creation(self, text: str):
        match = re.findall(": (.*) joined the game", text)
        if match:
            return f"{match[0]} が参加しました"

        match = re.findall(": (.*) left the game", text)
        if match:
            return f"{match[0]} が退出しました"

        return None

    def get_log(self, filepath: str):
        with open(filepath, "r", errors="ignore") as f:
            f.seek(self.log_position)
            logs = f.readlines()
            self.log_position = f.tell()

        for log in logs:
            text = self.message_creation(log)
            if text:
                self.send_message(text)

class ChangeHandler(FileSystemEventHandler):
    def __init__(self, monitor: MinecraftLogMonitor):
        self.monitor = monitor

    def on_modified(self, event):
        filepath = event.src_path
        if os.path.isfile(filepath) and os.path.basename(filepath) == self.monitor.target_file:
            self.monitor.get_log(filepath)

if __name__ == "__main__":
    monitor = MinecraftLogMonitor(TARGET_DIR, TARGET_FILE, WEBHOOK_URL)
    event_handler = ChangeHandler(monitor)
    observer = PollingObserver()
    observer.schedule(event_handler, monitor.target_dir, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
