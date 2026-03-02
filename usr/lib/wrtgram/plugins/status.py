#!/usr/bin/env python3
"""
status.py – Router status plugin (replaces shell plugins/status)

Prints emoji-formatted router status: uptime, load, RAM, CPU temp.
"""

import os
import sys


def _read_file(path: str, default: str = "") -> str:
    try:
        with open(path) as f:
            return f.read().strip()
    except (OSError, FileNotFoundError):
        return default


def _uptime_load() -> tuple[str, str]:
    """Parse /proc/uptime and /proc/loadavg."""
    raw = _read_file("/proc/uptime", "0 0").split()
    seconds = float(raw[0]) if raw else 0.0
    days    = int(seconds // 86400)
    hours   = int((seconds % 86400) // 3600)
    mins    = int((seconds % 3600) // 60)

    parts = []
    if days:
        parts.append(f"{days}d")
    if hours:
        parts.append(f"{hours}h")
    parts.append(f"{mins}m")
    uptime_str = " ".join(parts) or "0m"

    load_raw = _read_file("/proc/loadavg", "0 0 0").split()
    load_str = ", ".join(load_raw[:3]) if len(load_raw) >= 3 else "N/A"
    return uptime_str, load_str


def _mem_usage() -> tuple[int, int, int, int]:
    """Return (total_kb, used_kb, free_kb, percent) from /proc/meminfo."""
    info: dict[str, int] = {}
    for line in _read_file("/proc/meminfo").splitlines():
        parts = line.split()
        if len(parts) >= 2:
            info[parts[0].rstrip(":")] = int(parts[1])
    total   = info.get("MemTotal",     0)
    free    = info.get("MemFree",      0)
    buffers = info.get("Buffers",      0)
    cached  = info.get("Cached",       0)
    used    = total - free - buffers - cached
    percent = int(used * 100 / total) if total else 0
    return total, used, free, percent


def _progress_bar(percent: int, width: int = 10) -> str:
    filled = round(percent / 100 * width)
    return "█" * filled + "░" * (width - filled)


def _cpu_temp() -> str:
    raw = _read_file("/sys/class/thermal/thermal_zone0/temp")
    if raw and raw.isdigit():
        return f"{int(raw) / 1000:.1f}°C"
    return "N/A"


def _storage() -> str:
    try:
        st = os.statvfs("/overlay")
        total = st.f_blocks * st.f_frsize
        free  = st.f_bfree  * st.f_frsize
        used  = total - free
        pct   = int(used * 100 / total) if total else 0
        return f"{used // 1024 // 1024}MB / {total // 1024 // 1024}MB ({pct}%)"
    except Exception:
        return "N/A"


def main() -> None:
    uptime_str, load_str = _uptime_load()
    total_kb, used_kb, free_kb, mem_pct = _mem_usage()
    cpu_temp = _cpu_temp()
    storage  = _storage()

    mem_bar = _progress_bar(mem_pct)

    # Convert KB → MB for display
    total_mb = total_kb // 1024
    used_mb  = used_kb  // 1024
    free_mb  = free_kb  // 1024

    print(
        f"📊 *Router Status*\n\n"
        f"🕒 *Uptime:* {uptime_str}\n"
        f"⚙️ *CPU Load:* {load_str}\n"
        f"🌡️ *CPU Temp:* {cpu_temp}\n"
        f"🧠 *RAM:* `{mem_bar}` {mem_pct}%\n"
        f"   _{used_mb}MB used / {free_mb}MB free / {total_mb}MB total_\n"
        f"💾 *Storage:* {storage}"
    )


if __name__ == "__main__":
    main()
