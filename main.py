import os
import re
import time

import requests
from watchdog.events import FileSystemEventHandler
from watchdog.observers.polling import PollingObserver

from config.app import TARGET_DIR, TARGET_FILE, WEBHOOK_URL


def SendMessage(message: str) -> None:
    # discord以外のサービスのwebhookの場合はここを変更してください
    main_content = {"content": message}
    requests.post(WEBHOOK_URL, main_content)


def MessageCreation(text: str):
    # 参加,退出以外のメッセージが必要な場合はここに書く
    mach = re.findall(": (.*) joined the game", text)
    if len(mach) == 1:
        return str(mach[0]) + " が参加しました"

    mach = re.findall(": (.*) left the game", text)
    if len(mach) == 1:
        return str(mach[0]) + " が退出しました"

    return None


def GetLog(filepath: str):
    # 最終行のテキストを取得
    with open(filepath, "r") as f:
        endtxt = f.readlines()[-1]

    # 送信メッセージ作成
    text = MessageCreation(endtxt)

    if text is not None:
        SendMessage(text)


class ChangeHandler(FileSystemEventHandler):
    # フォルダ変更時のイベント
    def on_modified(self, event):
        filepath = event.src_path

        # ファイルでない場合無視する
        if os.path.isfile(filepath) is False:
            return

        # 監視対応のファイルでない場合無視する
        filename = os.path.basename(filepath)
        if filename != TARGET_FILE:
            return

        GetLog(filepath)


if __name__ in "__main__":
    while 1:
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
