#!/usr/bin/env python3
"""
lanports.py – LAN port / DHCP event monitor daemon (replaces sbin/lanports)

Tails `logread -f` asynchronously, parses:
  • Switch port up/down events   → LAN Port Alert
  • DHCP ACK events              → New Device Connected

Usage:
    python3 /sbin/lanports.py &
"""

import asyncio
import logging
import re
import subprocess
import sys
from datetime import datetime

sys.path.insert(0, "/usr/lib/wrtgram")
from wrtgramlib import get_config, send_message, subprocess_cmd

import telegram

logging.basicConfig(
    format="%(asctime)s [lanports] %(levelname)s: %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger("lanports")

# Regex patterns
_PORT_PATTERN  = re.compile(r"Port (\d+) is (up|down)", re.IGNORECASE)
_IP_MAC_PATTERN = re.compile(
    r"(\d{1,3}(?:\.\d{1,3}){3})\s+"
    r"([0-9a-fA-F]{2}(?::[0-9a-fA-F]{2}){5})"
    r"(?:\s+(\S+))?"
)


def _get_switch_name() -> str:
    result = subprocess_cmd(["swconfig", "list"])
    # e.g. "Found: switch0 - rtl8366rb"
    m = re.search(r"Found: (\S+)", result)
    return m.group(1) if m else "switch0"


def _is_mac_ignored(mac: str, ignored_file: str) -> bool:
    """Return True if *mac* is in the ignore list."""
    try:
        with open(ignored_file) as f:
            return mac.lower() in f.read().lower()
    except FileNotFoundError:
        return False


async def _tail_logread(
    bot: telegram.Bot,
    chat_id: str,
    ignored_macaddrs_file: str,
) -> None:
    """Tail logread -f and react to port / DHCP events."""
    switch = _get_switch_name()
    logger.info("Tailing logread -f (switch=%s)", switch)

    proc = await asyncio.create_subprocess_exec(
        "logread", "-f",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.DEVNULL,
    )

    # State machine for DHCP: offer → ack
    pending_offer = False
    offer_countdown = 0

    async for raw_line in proc.stdout:
        try:
            line = raw_line.decode(errors="replace").rstrip()
        except Exception:
            continue

        # ── LAN port state ──────────────────────────────────────────────
        if switch in line:
            m = _PORT_PATTERN.search(line)
            if m:
                port_num = m.group(1)
                state    = m.group(2).lower()
                icon     = "🟢" if state == "up" else "🔴"
                time_str = datetime.now().strftime("%I:%M:%S %p")
                text = (
                    f"{icon} *LAN Port Alert* {icon}\n\n"
                    f"*Port:* {port_num}\n"
                    f"*Time:* {time_str}\n"
                    f"*State:* {state}"
                )
                logger.info("Port %s is %s", port_num, state)
                await send_message(bot, chat_id, text)

        # ── DHCP OFFER (precursor) ───────────────────────────────────────
        if "DHCPOFFER" in line:
            pending_offer   = True
            offer_countdown = 4

        # ── DHCP ACK (new device) ────────────────────────────────────────
        if "DHCPACK" in line and pending_offer:
            m = _IP_MAC_PATTERN.search(line)
            if m:
                ip       = m.group(1)
                mac      = m.group(2).lower()
                hostname = m.group(3) or "N/A"
                if hostname in ("*", ""):
                    hostname = "N/A"

                if not _is_mac_ignored(mac, ignored_macaddrs_file):
                    time_str = datetime.now().strftime("%I:%M:%S %p")
                    text = (
                        "🆕 *New Device Connected* 🆕\n\n"
                        f"*Hostname:* {hostname}\n"
                        f"*Time:* {time_str}\n"
                        f"*IP Address:* {ip}\n"
                        f"*MAC Address:* {mac.upper()}"
                    )
                    logger.info("New device: %s %s %s", hostname, ip, mac)
                    await send_message(bot, chat_id, text)
                else:
                    logger.info("Ignored MAC: %s", mac)

            pending_offer = False

        # Decrement offer countdown
        if offer_countdown > 0:
            offer_countdown -= 1
            if offer_countdown == 0:
                pending_offer = False


async def main() -> None:
    cfg = get_config()
    if not cfg.get("key"):
        logger.error("Bot token not configured.")
        sys.exit(1)

    bot = telegram.Bot(token=cfg["key"])

    while True:
        try:
            await _tail_logread(
                bot,
                cfg["my_chat_id"],
                cfg["ignored_macaddrs_file"],
            )
        except Exception as exc:
            logger.error("lanports crash: %s — restarting in 5s", exc)
            await asyncio.sleep(5)


if __name__ == "__main__":
    asyncio.run(main())
