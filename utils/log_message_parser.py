import re

MESSAGE_PATTERNS = [
    (": (.*) joined the game", "{0} が参加しました"),
    (": (.*) left the game", "{0} が退出しました"),
    # 今後新しいイベントがあればここに追加
]


def message_creation(text: str):
    for pattern, message_format in MESSAGE_PATTERNS:
        match = re.search(pattern, text)
        if match:
            return message_format.format(*match.groups())
    return None
