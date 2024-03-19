import copy
import os
import re
import time

import requests
from watchdog.events import FileSystemEventHandler
from watchdog.observers.polling import PollingObserver

from config.app import TARGET_DIR, TARGET_FILE, WEBHOOK_URL

# prevの内容をファイルレベルで保持するための変更
prev_logs = []


def SendMessage(message: str) -> None:
    main_content = {"content": message}
    requests.post(WEBHOOK_URL, main_content)


def MessageCreation(text: str):
    match = re.findall(": (.*) joined the game", text)
    if len(match) == 1:
        return str(match[0]) + " が参加しました"

    match = re.findall(": (.*) left the game", text)
    if len(match) == 1:
        return str(match[0]) + " が退出しました"

    return None


def GetLog(filepath: str):
    global prev_logs  # グローバル変数を使用する代わりにファイルレベルの変数を更新

    with open(filepath, "r", errors="ignore") as f:
        logs = f.readlines()

    old_logs = copy.deepcopy(prev_logs)
    prev_logs = copy.deepcopy(logs)

    del logs[: len(old_logs)]

    for log in logs:
        text = MessageCreation(log)
        if text is not None:
            SendMessage(text)


class ChangeHandler(FileSystemEventHandler):
    def on_modified(self, event):
        filepath = event.src_path
        if os.path.isfile(filepath) and os.path.basename(filepath) == TARGET_FILE:
            GetLog(filepath)


if __name__ == "__main__":
    with open(TARGET_DIR + "/" + TARGET_FILE, "r", errors="ignore") as f:
        prev_logs = f.readlines()

    event_handler = ChangeHandler()
    observer = PollingObserver()
    observer.schedule(event_handler, TARGET_DIR, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
