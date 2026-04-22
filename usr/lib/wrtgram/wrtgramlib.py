#!/usr/bin/env python3
"""
wrtgramlib.py – Shared helpers for the WrtGram Python bot.

Provides:
  - get_config()      : Read UCI config and return a dict.
  - send_message()    : Chunked async Telegram message sender.
  - run_plugin()      : Call a plugin script and return its stdout.
  - subprocess_cmd()  : Thin logged wrapper around subprocess.run.
"""

import asyncio
import logging
import subprocess
from typing import Optional

import telegram

logger = logging.getLogger("wrtgramlib")

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

def _uci(key: str) -> str:
    """Read a single UCI option; return empty string on failure."""
    result = subprocess.run(
        ["uci", "-q", "get", key],
        capture_output=True, text=True
    )
    return result.stdout.strip()


def get_config() -> dict:
    """Return WrtGram config as a dict with keys:
    key, url, api, my_chat_id, timeout, ignored_macaddrs_file,
    smtp_from, smtp_to, openrouter_key, openrouter_model.
    """
    url = _uci("wrtgram.global.url")
    key = _uci("wrtgram.global.key")
    return {
        "key": key,
        "url": url,
        "api": f"{url}{key}",
        "my_chat_id": _uci("wrtgram.global.my_chat_id"),
        "timeout": int(_uci("wrtgram.global.timeout") or "60"),
        "ignored_macaddrs_file": _uci("wrtgram.global.ignored_macaddrs_file"),
        "smtp_from": _uci("wrtgram.smtp.from"),
        "smtp_to": _uci("wrtgram.smtp.to"),
        "openrouter_key": _uci("wrtgram.global.openrouter_key"),
        "openrouter_model": _uci("wrtgram.global.openrouter_model") or "meta-llama/llama-3.1-8b-instruct:free",
    }


def get_plugins_context() -> str:
    """Read all plugin help files to provide context for the AI."""
    import os
    help_dir = "/usr/lib/wrtgram/plugins/help"
    context = ["Available WrtGram Plugins:"]
    try:
        if os.path.exists(help_dir):
            for f in sorted(os.listdir(help_dir)):
                help_file = os.path.join(help_dir, f)
                if os.path.isfile(help_file):
                    with open(help_file, "r") as fh:
                        desc = fh.read().strip()
                        context.append(f"- {f}: {desc}")
    except Exception as e:
        logger.error("Error gathering plugins context: %s", e)
    return "\n".join(context)

# ---------------------------------------------------------------------------
# Message Sending
# ---------------------------------------------------------------------------

MAX_MSG_LEN = 4096


async def send_message(
    bot: telegram.Bot,
    chat_id: str | int,
    text: str,
    parse_mode: str = "Markdown",
    reply_markup=None,
) -> None:
    """Send *text* to *chat_id*, splitting into chunks ≤ 4096 chars."""
    if not text or not text.strip():
        return

    # Split on newlines to avoid cutting markdown mid-word
    lines = text.splitlines(keepends=True)
    chunk = ""
    for line in lines:
        if len(chunk) + len(line) > MAX_MSG_LEN:
            await bot.send_message(
                chat_id=chat_id,
                text=chunk,
                parse_mode=parse_mode,
            )
            chunk = line
        else:
            chunk += line

    if chunk.strip():
        await bot.send_message(
            chat_id=chat_id,
            text=chunk,
            parse_mode=parse_mode,
            reply_markup=reply_markup,
        )


# ---------------------------------------------------------------------------
# Plugin / subprocess helpers
# ---------------------------------------------------------------------------

def subprocess_cmd(cmd: list[str], cwd: Optional[str] = None) -> str:
    """Run *cmd*, log it, return stdout. Stderr is discarded."""
    logger.info("Running: %s", " ".join(cmd))
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=cwd,
    )
    if result.returncode != 0:
        logger.warning("Command %s exited %d: %s", cmd[0], result.returncode, result.stderr[:200])
    return result.stdout


def run_plugin(plugin_path: str, params: str = "") -> str:
    """Execute a plugin script and return its stdout text.
    
    *plugin_path* is the absolute path to the plugin script.
    *params* is an optional space-separated parameter string.
    """
    cmd = [plugin_path]
    if params:
        cmd += params.split()
    return subprocess_cmd(cmd, cwd=str(plugin_path).rsplit("/", 1)[0])


# ---------------------------------------------------------------------------
# Email alert (unauthorized users)
# ---------------------------------------------------------------------------

def send_email_alert(
    smtp_from: str,
    smtp_to: str,
    username: str,
    fullname: str,
    command: str,
) -> None:
    """Send a warning e-mail via ssmtp when an unauthorized user hits the bot."""
    try:
        body = (
            f"From: {smtp_from}\n"
            f"To: {smtp_to}\n"
            f"Subject: TelegramBOT\n\n"
            f"Someone with username {username} ({fullname}) "
            f"is trying to use your bot, sending the {command}"
        )
        proc = subprocess.run(
            ["ssmtp", smtp_to],
            input=body,
            text=True,
            capture_output=True,
        )
        if proc.returncode != 0:
            logger.warning("ssmtp failed: %s", proc.stderr)
    except Exception as exc:
        logger.error("Email alert failed: %s", exc)
