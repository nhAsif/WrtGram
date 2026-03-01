#!/usr/bin/env python3
import sys, os, json

sys.path.append("/usr/lib/wrtgram")
sys.path.append("/usr/lib/wrtgram/plugins")
from dashboard import run_dashboard

if __name__ == "__main__":
    text = run_dashboard()
    keyboard = {
        "inline_keyboard": [
            [{"callback_data": "dashboard|", "text": "🔄 Refresh"}],
            [{"callback_data": "reboot|", "text": "♻️ Reboot"}]
        ]
    }
    print(f"1|{text}|{json.dumps(keyboard)}")
