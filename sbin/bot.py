#!/usr/bin/env python3
"""
bot.py – WrtGram Telegram Bot (Python rewrite)

Replaces: sbin/telegram_bot, sbin/telebot, sbin/telegram_sender, sbin/typing

Usage:
    python3 /sbin/bot.py

Dependencies (opkg / pip3):
    python3-telegram  (python-telegram-bot >= 20.x)
"""

import asyncio
import json
import logging
import os
import random
import re
import sys

# Allow importing wrtgramlib from its installed location
sys.path.insert(0, "/usr/lib/wrtgram")

from telegram import (
    Bot,
    BotCommand,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    Update,
)
from telegram.constants import ChatAction, ParseMode
from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from wrtgramlib import (
    get_config,
    run_plugin,
    send_email_alert,
    send_message,
    subprocess_cmd,
)

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger("bot")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
PLUGINS_DIR = "/usr/lib/wrtgram/plugins"
ACTIONS_DIR = "/usr/lib/wrtgram/plugins/actions"
HELP_DIR    = "/usr/lib/wrtgram/plugins/help"

# ---------------------------------------------------------------------------
# Global config (loaded once at startup)
# ---------------------------------------------------------------------------
CFG: dict = {}


# ---------------------------------------------------------------------------
# Auth helpers
# ---------------------------------------------------------------------------

def is_authorized(update: Update) -> bool:
    """Return True if the message/callback comes from MY_CHAT_ID."""
    chat_id = None
    if update.message:
        chat_id = str(update.message.chat_id)
    elif update.callback_query:
        chat_id = str(update.callback_query.message.chat_id)
    return chat_id == CFG.get("my_chat_id", "")


async def handle_unauthorized(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Warn the owner by email, tell the intruder this is private, and leave."""
    msg = update.message
    if not msg:
        return
    user = msg.from_user
    username  = user.username  or "N/A"
    full_name = f"{user.first_name or ''} {user.last_name or ''}".strip()
    command   = msg.text or ""

    send_email_alert(
        CFG.get("smtp_from", ""),
        CFG.get("smtp_to",   ""),
        username,
        full_name,
        command,
    )

    await context.bot.send_message(
        chat_id=msg.chat_id,
        reply_to_message_id=msg.message_id,
        text="This is a private bot. "
             "If you want to set up your own, see https://github.com/nhAsif/WrtGram",
        parse_mode=ParseMode.MARKDOWN,
    )
    try:
        await context.bot.leave_chat(msg.chat_id)
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Typing indicator
# ---------------------------------------------------------------------------

async def send_typing(context: ContextTypes.DEFAULT_TYPE, chat_id: int | str) -> None:
    try:
        await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Keyboards & Menus
# ---------------------------------------------------------------------------

def get_main_menu_keyboard() -> ReplyKeyboardMarkup:
    """Bottom persistent menu."""
    keyboard = [
        ["📊 Status", "🌐 WiFi"],
        ["🛡️ Firewall", "🛠️ Help"],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


# ---------------------------------------------------------------------------
# /start command
# ---------------------------------------------------------------------------

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_authorized(update):
        await handle_unauthorized(update, context)
        return

    await send_typing(context, update.effective_chat.id)
    name = update.effective_user.first_name or "there"
    
    greetings = [
        f"👋 *Hello, {name}!*",
        f"🚀 *Welcome back, {name}!*",
        f"🛡️ *WrtGram at your service, {name}!*",
        f"⚙️ *System online. Greetings, {name}!*",
    ]
    
    text = (
        f"{random.choice(greetings)}\n\n"
        "I am your *OpenWrt* companion. I'll help you monitor and manage your router with ease.\n\n"
        "✨ *Quick Actions:*\n"
        "• Check status with 📊 *Status*\n"
        "• Manage 🌐 *WiFi* or 🛡️ *Firewall*\n"
        "• Explore all commands via /help\n\n"
        "What shall we do today?"
    )
    await update.message.reply_text(
        text, 
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=get_main_menu_keyboard()
    )


# ---------------------------------------------------------------------------
# /help command
# ---------------------------------------------------------------------------

async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_authorized(update):
        await handle_unauthorized(update, context)
        return

    await send_typing(context, update.effective_chat.id)

    categories = {
        "📊 *Status & Info*": ["status", "get_ip", "get_mac", "get_ping", "get_uptime", "hst_list", "lan_scan", "netstat", "swports_list"],
        "🌐 *WiFi Management*": ["wifi_list", "wifi_enable", "wifi_disable", "wifi_restart", "wll_list"],
        "🛡️ *Firewall & Security*": ["fw_list", "fw_add", "fw_delete", "fw_enable", "fw_disable", "fw_unblock", "fwr_list", "fwr_enable", "fwr_disable", "ignoredmac_list", "ignoredmac_add"],
        "🔌 *Network Interfaces*": ["interfaces_list", "interface_up", "interface_down", "interface_restart"],
        "⚙️ *System & Processes*": ["proc_list", "proc_start", "proc_stop", "proc_restart", "reboot", "opkg_update", "opkg_install", "tmate", "cf_tunnel", "cf_tunnel_stop"],
    }

    lines = ["🛠 *WrtGram Help Menu*\n"]
    
    try:
        all_plugins = [f for f in os.listdir(PLUGINS_DIR) if os.path.isfile(os.path.join(PLUGINS_DIR, f))]
        categorized = []

        for cat_name, p_list in categories.items():
            cat_lines = []
            for p in sorted(p_list):
                if p in all_plugins:
                    help_file = os.path.join(HELP_DIR, p)
                    desc = "No description."
                    if os.path.isfile(help_file):
                        with open(help_file) as fh:
                            desc = fh.read().strip()
                    cat_lines.append(f"• [/{p}](/{p}) – {desc}")
                    categorized.append(p)
            
            if cat_lines:
                lines.append(f"\n{cat_name}")
                lines.extend(cat_lines)

        # Handle uncategorized plugins
        others = sorted([p for p in all_plugins if p not in categorized and p != "start"])
        if others:
            lines.append("\n📦 *Other Commands*")
            for p in others:
                help_file = os.path.join(HELP_DIR, p)
                desc = "No description."
                if os.path.isfile(help_file):
                    with open(help_file) as fh:
                        desc = fh.read().strip()
                lines.append(f"• [/{p}](/{p}) – {desc}")

    except Exception as exc:
        logger.error("Error building help: %s", exc)
        lines.append("\n_(Could not load command list.)_")

    await send_message(
        context.bot,
        update.effective_chat.id,
        "\n".join(lines),
    )


# ---------------------------------------------------------------------------
# Inline keyboard builders (replaces ctx/ shell scripts)
# ---------------------------------------------------------------------------

def _build_fw_keyboard(action_cmd: str) -> InlineKeyboardMarkup:
    """Build inline keyboard with firewall rules (replaces ctx/fw_list)."""
    raw = subprocess_cmd(["uci", "-q", "show", "firewall"])
    buttons = []
    for line in raw.splitlines():
        if "@rule" not in line or ".name=" not in line:
            continue
        # Extract rule index and name
        m = re.search(r"@rule\[(\d+)\]\.name='([^']+)'", line)
        if not m:
            continue
        idx, name = m.group(1), m.group(2)
        # Check enabled state
        enabled_raw = subprocess_cmd(["uci", "-q", "get", f"firewall.@rule[{idx}].enabled"])
        state = "(Disabled)" if enabled_raw.strip() == "0" else "(Enabled)"
        callback_data = f"{action_cmd}|{idx}^{name}"
        buttons.append([InlineKeyboardButton(f"{name} {state}", callback_data=callback_data)])
    return InlineKeyboardMarkup(buttons)


def _build_wifi_keyboard(action_cmd: str) -> InlineKeyboardMarkup:
    """Build inline keyboard with WiFi networks (replaces ctx/wifi_list)."""
    raw = subprocess_cmd(["uci", "-q", "show", "wireless"])
    buttons = []
    for line in raw.splitlines():
        m = re.search(r"default_radio(\d+)\.ssid='([^']+)'", line)
        if not m:
            continue
        idx, ssid = m.group(1), m.group(2)
        toggle = subprocess_cmd(["uci", "-q", "-q", "get", f"wireless.radio{idx}.__toggle"])
        state = "(Disabled)" if toggle.strip() == "Disable" else "(Enabled)"
        callback_data = f"{action_cmd}|{idx}^{ssid}"
        buttons.append([InlineKeyboardButton(f"{ssid} {state}", callback_data=callback_data)])
    return InlineKeyboardMarkup(buttons)


def _build_interfaces_keyboard(action_cmd: str) -> InlineKeyboardMarkup:
    """Build inline keyboard with network interfaces (replaces ctx/interfaces_list)."""
    raw = subprocess_cmd(["ubus", "call", "network.interface", "dump"])
    buttons = []
    try:
        data = json.loads(raw)
        for iface in data.get("interface", []):
            name = iface.get("interface", "")
            if name:
                callback_data = f"{action_cmd}|{name}^"
                buttons.append([InlineKeyboardButton(name, callback_data=callback_data)])
    except Exception as exc:
        logger.error("interfaces keyboard error: %s", exc)
    return InlineKeyboardMarkup(buttons)


def _build_reboot_keyboard() -> InlineKeyboardMarkup:
    """Confirm/cancel keyboard for reboot."""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Yes, Reboot!", callback_data="reboot|confirm^"),
            InlineKeyboardButton("❌ Cancel",       callback_data="reboot|cancel^"),
        ]
    ])


def _build_status_keyboard() -> InlineKeyboardMarkup:
    """Add a refresh button to the status message."""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔄 Refresh Status", callback_data="refresh_status|")]
    ])


# Commands that need an inline keyboard (map command → builder fn)
_KEYBOARD_COMMANDS: dict = {
    "/fw_list":         ("fw_list",         _build_fw_keyboard),
    "/fwr_list":        ("fwr_list",        _build_fw_keyboard),       # reuse fw keyboard shape
    "/wifi_list":       ("wifi_list",       _build_wifi_keyboard),
    "/interfaces_list": ("interfaces_list", _build_interfaces_keyboard),
    "/reboot":          (None,              lambda _: _build_reboot_keyboard()),
    "/status":          (None,              lambda _: _build_status_keyboard()),
}


# ---------------------------------------------------------------------------
# Generic plugin dispatcher
# ---------------------------------------------------------------------------

async def dispatch_plugin(update: Update, context: ContextTypes.DEFAULT_TYPE, command: str = None) -> None:
    """Route any slash-command to its plugin script."""
    if not is_authorized(update):
        await handle_unauthorized(update, context)
        return

    if command:
        cmd = command
        params = ""
    else:
        text   = update.message.text or ""
        parts  = text.split(None, 1)
        cmd    = parts[0].lower().split("@")[0]   # strip /cmd@botname
        params = parts[1].strip() if len(parts) > 1 else ""
    
    # Sanitise params (strip shell-dangerous chars)
    params = "".join(c for c in params if c not in '&;\\><|"\'')

    await send_typing(context, update.effective_chat.id)

    plugin_path = os.path.join(PLUGINS_DIR, cmd.lstrip("/"))

    if not os.path.isfile(plugin_path):
        await update.message.reply_text(
            f"Command *{cmd}* not found!", parse_mode=ParseMode.MARKDOWN
        )
        return

    logger.info("Dispatching plugin: %s params=%r", cmd, params)

    # Send a "Processing" message for better UX
    processing_msg = await update.message.reply_text(
        f"⏳ *Processing /{cmd.lstrip('/')}...*",
        parse_mode=ParseMode.MARKDOWN
    )

    # Commands that also get an inline keyboard
    keyboard = None
    if cmd in _KEYBOARD_COMMANDS:
        action_cmd, builder_fn = _KEYBOARD_COMMANDS[cmd]
        keyboard = builder_fn(action_cmd)

    result = run_plugin(plugin_path, params)
    
    # Remove the processing message
    try:
        await processing_msg.delete()
    except Exception:
        pass

    # Special handling for AI command: parse and execute tags
    if cmd == "/ai":
        # 1. Handle Plugin Creation
        plugin_matches = re.findall(r"\[CREATE_PLUGIN:\s*(\w+)\](.*?)\[/CREATE_PLUGIN\]", result, re.DOTALL)
        for p_name, p_content in plugin_matches:
            p_path = os.path.join(PLUGINS_DIR, p_name)
            try:
                with open(p_path, "w") as f:
                    f.write(p_content.strip())
                os.chmod(p_path, 0o755)
                await send_message(context.bot, update.effective_chat.id, f"✅ *Plugin Created:* `/{p_name}`")
            except Exception as e:
                await send_message(context.bot, update.effective_chat.id, f"❌ *Error creating plugin {p_name}:* {e}")

        # 2. Handle Help File Creation
        help_matches = re.findall(r"\[CREATE_HELP:\s*(\w+)\](.*?)\[/CREATE_HELP\]", result, re.DOTALL)
        for h_name, h_content in help_matches:
            h_path = os.path.join(HELP_DIR, h_name)
            try:
                with open(h_path, "w") as f:
                    f.write(h_content.strip())
            except Exception as e:
                logger.error("Error creating help for %s: %s", h_name, e)

        # 3. Handle Execution tags (existing logic)
        if "[EXEC:" in result:
            # Send the AI's explanation first
            await send_message(context.bot, update.effective_chat.id, result)
            
            # Extract and run commands
            commands = re.findall(r"\[EXEC:\s*(.*?)\]", result)
            for c in commands:
                c = c.strip()
                # If it's a plugin, run it via run_plugin, otherwise use subprocess_cmd
                plugin_name = c.split()[0]
                full_plugin_path = os.path.join(PLUGINS_DIR, plugin_name)
                
                await send_message(context.bot, update.effective_chat.id, f"🛠 *Executing:* `{c}`")
                
                if os.path.isfile(full_plugin_path):
                    exec_result = run_plugin(full_plugin_path, " ".join(c.split()[1:]))
                else:
                    exec_result = subprocess_cmd(c.split())
                
                await send_message(context.bot, update.effective_chat.id, exec_result or "_(done)_")
            return
        
        # If no execution tags but we had a result, send it
        if result:
            await send_message(context.bot, update.effective_chat.id, result)
        return

    # Send the actual result (supports chunking via send_message)
    await send_message(
        context.bot,
        update.effective_chat.id,
        result or "_(no output)_",
        reply_markup=keyboard,
    )


# ---------------------------------------------------------------------------
# Callback query dispatcher (inline keyboard buttons)
# ---------------------------------------------------------------------------

async def dispatch_action(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle inline keyboard button presses (replaces actions/ shell scripts)."""
    query = update.callback_query
    await query.answer()

    if not is_authorized(update):
        await query.answer("Unauthorized.", show_alert=True)
        return

    data = query.data or ""
    # Format: "action_cmd|param1^param2"
    if "|" not in data:
        return

    action_name, raw_params = data.split("|", 1)
    params = raw_params.replace("^", " ").strip()
    params = "".join(c for c in params if c not in '&;\\><|"\'')

    # Special built-in actions
    if action_name == "reboot":
        if "confirm" in params:
            await query.edit_message_text("♻️ Rebooting in 15 seconds...")
            subprocess_cmd(["sh", "-c", "sleep 15 && reboot &"])
        else:
            await query.edit_message_text("❌ Reboot cancelled.")
        return

    if action_name == "refresh_status":
        plugin_path = os.path.join(PLUGINS_DIR, "status")
        result = run_plugin(plugin_path)
        try:
            await query.edit_message_text(
                result or "_(no output)_",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=_build_status_keyboard()
            )
        except Exception as exc:
            # Likely message is identical, just ignore
            logger.debug("Refresh status edit failed: %s", exc)
        return

    action_path = os.path.join(ACTIONS_DIR, action_name)
    if not os.path.isfile(action_path):
        await query.answer(f"Action {action_name} not found.", show_alert=True)
        return

    logger.info("Dispatching action: %s params=%r", action_name, params)
    raw_result = run_plugin(action_path, params)

    # Actions return "remove_flag|message" (legacy format)
    if "|" in raw_result:
        remove_flag, msg = raw_result.split("|", 1)
    else:
        remove_flag, msg = "0", raw_result

    await query.answer(msg.strip()[:200])   # popup toast
    if remove_flag.strip() == "1":
        try:
            await query.edit_message_text(msg.strip() or "Done.")
        except Exception:
            pass


# ---------------------------------------------------------------------------
# Menu button handler
# ---------------------------------------------------------------------------

async def handle_menu_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Map ReplyKeyboardMarkup button text to commands."""
    if not is_authorized(update):
        await handle_unauthorized(update, context)
        return

    text = update.message.text
    mapping = {
        "📊 Status":   "/status",
        "🌐 WiFi":     "/wifi_list",
        "🛡️ Firewall": "/fw_list",
        "🛠️ Help":     "/help",
    }

    if text == "🛠️ Help":
        await cmd_help(update, context)
    elif text in mapping:
        # Pass the mapped command explicitly
        await dispatch_plugin(update, context, command=mapping[text])
    else:
        await unknown_text(update, context)


# ---------------------------------------------------------------------------
# Unknown non-command text
# ---------------------------------------------------------------------------

async def unknown_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_authorized(update):
        await handle_unauthorized(update, context)
        return

    await update.message.reply_text(
        "Sorry, I only recognize *commands*.\n"
        "Commands start with a slash. Send /help to see them all.",
        parse_mode=ParseMode.MARKDOWN,
    )


# ---------------------------------------------------------------------------
# Bot startup notification
# ---------------------------------------------------------------------------

async def post_init(application) -> None:
    """Send a startup message to the owner and set bot commands."""
    try:
        # 1. Set bot commands for the menu button
        commands = [
            BotCommand("start",  "Start the bot & show menu"),
            BotCommand("help",   "List all available commands"),
            BotCommand("status", "Show router status (CPU, RAM, etc)"),
            BotCommand("wifi_list", "Manage WiFi networks"),
            BotCommand("fw_list", "Manage Firewall rules"),
        ]
        await application.bot.set_my_commands(commands)

        # 2. Notify the owner
        await application.bot.send_message(
            chat_id=CFG["my_chat_id"],
            text="✅ *WrtGram bot started!*\nSend /help to see what I can do.",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=get_main_menu_keyboard()
        )
    except Exception as exc:
        logger.warning("post_init failed: %s", exc)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    global CFG
    CFG = get_config()

    if not CFG.get("key"):
        logger.error("Bot token not configured. Set wrtgram.global.key via UCI.")
        sys.exit(1)

    logger.info("Starting WrtGram bot (my_chat_id=%s)", CFG.get("my_chat_id"))

    app = (
        ApplicationBuilder()
        .token(CFG["key"])
        .post_init(post_init)
        .build()
    )

    # Command handlers
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help",  cmd_help))

    # All other commands → plugin dispatcher
    app.add_handler(MessageHandler(filters.COMMAND, dispatch_plugin))

    # Inline keyboard callbacks
    app.add_handler(CallbackQueryHandler(dispatch_action))

    # Menu buttons and other text
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_menu_buttons))

    # Start polling (drop updates older than bot start time)
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
