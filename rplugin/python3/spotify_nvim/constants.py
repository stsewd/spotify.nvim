OPTIONS = [
    ("play/pause", "toggle"),
    ("next", "next"),
    ("prev", "prev"),
    ("play", "play"),
    ("pause", "pause"),
    ("stop", "stop"),
    ("show", "show_window"),
    ("status", "_show_current_status"),
]

SYMBOLS_REPR = {
    "playing": {
        "text": "[playing]",
        "ascii": "►",
        "emoji": "▶️",
    },
    "paused": {
        "text": "[paused]",
        "ascii": "■",
        "emoji": "⏸️",
    },
    "stopped": {
        "text": "[stopped]",
        "ascii": "■",
        "emoji": "⏸️",
    },
    "music": {
        "text": "",
        "ascii": "♫♪",
        "emoji": "🎶",
    },
}
