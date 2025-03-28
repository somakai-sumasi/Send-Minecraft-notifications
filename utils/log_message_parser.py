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
            return remove_formatting(message_format.format(*match.groups()))
    return None


def remove_formatting(text):
    """
    装飾に使われる「§」とその直後の、0～9またはa～u（大文字小文字）の文字を削除する関数
    """
    pattern = r'§[0-9a-uA-U]'
    return re.sub(pattern, '', text)
