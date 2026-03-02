#!/usr/bin/env python3
"""
hosts_scan.py – Async ARP/Ping scanner daemon (replaces sbin/hosts_scan)

Reads ARP table, pings all known IPs in parallel via asyncio,
sends a Telegram notification on device state changes (UP ↔ DOWN).

Usage:
    python3 /sbin/hosts_scan.py &
"""

import asyncio
import logging
import os
import sys
from pathlib import Path

sys.path.insert(0, "/usr/lib/wrtgram")
from wrtgramlib import get_config, send_message

import telegram

logging.basicConfig(
    format="%(asctime)s [hosts_scan] %(levelname)s: %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger("hosts_scan")

STATE_DIR = Path("/var/run/wrtgram_arps")
SCAN_INTERVAL = 300  # seconds between full scans


def _get_arp_entries() -> list[tuple[str, str]]:
    """Return list of (ip, mac) from /proc/net/arp for the LAN subnet."""
    entries = []
    try:
        with open("/proc/net/arp") as f:
            next(f)  # skip header
            for line in f:
                parts = line.split()
                if len(parts) >= 4:
                    ip, mac = parts[0], parts[3]
                    # Ignore incomplete entries
                    if mac != "00:00:00:00:00:00":
                        entries.append((ip, mac))
    except Exception as exc:
        logger.error("ARP read error: %s", exc)
    return entries


def _get_hostname(ip: str) -> str:
    """Resolve IP to hostname from DHCP leases or static hosts."""
    try:
        with open("/tmp/dhcp.leases") as f:
            for line in f:
                if f" {ip} " in line:
                    parts = line.split()
                    if len(parts) >= 4 and parts[3] != "*":
                        return parts[3]
    except FileNotFoundError:
        pass
    try:
        with open("/tmp/hosts/dhcp.cfg01411c") as f:
            for line in f:
                if line.startswith(ip):
                    parts = line.split()
                    if len(parts) >= 2:
                        return parts[1]
    except FileNotFoundError:
        pass
    return ip


async def _ping(ip: str) -> bool:
    """Return True if *ip* responds to ping (1 packet, 1s timeout)."""
    try:
        proc = await asyncio.create_subprocess_exec(
            "ping", "-c", "1", "-w", "1", ip,
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.DEVNULL,
        )
        await proc.wait()
        return proc.returncode == 0
    except Exception:
        return False


async def _check_host(
    bot: telegram.Bot,
    chat_id: str,
    ip: str,
    mac: str,
) -> None:
    """Ping a single host and notify if state changed."""
    state_file = STATE_DIR / ip
    previous = state_file.read_text().strip() if state_file.exists() else "NULL"

    is_up = await _ping(ip)
    current = "UP" if is_up else "DOWN"

    if previous != current:
        hostname = _get_hostname(ip)
        from datetime import datetime
        date_str = datetime.now().strftime("%d/%m/%Y %I:%M %p")
        icon = "🟢" if is_up else "🔴"
        text = (
            f"📱 *Device:* {hostname}\n"
            f"📅 *Date:* {date_str}\n"
            f"🌐 *IP:* {ip}\n"
            f"🔢 *MAC:* {mac}\n"
            f"📶 *State:* {icon} {current}"
        )
        logger.info("State change: %s %s → %s", ip, previous, current)
        await send_message(bot, chat_id, text)

    state_file.write_text(current)


async def scan_loop(bot: telegram.Bot, chat_id: str) -> None:
    """Continuously scan ARP table and notify on changes."""
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    logger.info("hosts_scan started (interval=%ds)", SCAN_INTERVAL)

    while True:
        entries = _get_arp_entries()
        if entries:
            tasks = [_check_host(bot, chat_id, ip, mac) for ip, mac in entries]
            await asyncio.gather(*tasks)
        else:
            logger.debug("ARP table empty, nothing to scan.")
        await asyncio.sleep(SCAN_INTERVAL)


async def main() -> None:
    cfg = get_config()
    if not cfg.get("key"):
        logger.error("Bot token not configured.")
        sys.exit(1)

    bot = telegram.Bot(token=cfg["key"])
    await scan_loop(bot, cfg["my_chat_id"])


if __name__ == "__main__":
    asyncio.run(main())
