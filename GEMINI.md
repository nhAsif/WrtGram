# WrtGram: Telegram Bot for OpenWrt

WrtGram is a powerful, extensible Telegram bot designed specifically for managing and monitoring OpenWrt routers. It provides a remote interface to the router's command-line utilities (UCI, ubus, opkg, etc.) through a simple Telegram chat interface.

## Project Overview

*   **Main Bot Core:** An asynchronous Python daemon (`sbin/bot.py`) built with `python-telegram-bot` (v20+). It handles user authentication, command dispatching, and interactive inline keyboards.
*   **Monitoring Services:**
    *   `lanports.py`: Monitors router logs for LAN port status changes and DHCP leases.
    *   `hosts_scan.py`: Periodically scans the network for new devices and sends notifications.
*   **Clean Architecture:** Version 3.0 uses a consolidated Python-centric architecture, removing legacy shell wrappers and redundant context scripts.
*   **Technologies:** Python 3, Shell Scripting, OpenWrt UCI (Unified Configuration Interface), `ubus`, `curl`, and `jsonfilter`.

## Building and Running

### Build Command
The project is managed as an OpenWrt package. To compile the package:
```bash
# Within an OpenWrt SDK or buildroot environment
make package/wrtgram/compile V=s
```

### Installation
Transfer the generated `.ipk` file to your router and install it:
```bash
opkg install wrtgram_3.0-1_all.ipk
```

### Service Management
Services are managed via standard OpenWrt init scripts:
```bash
/etc/init.d/telegram_bot {start|stop|restart|enable|disable}
/etc/init.d/lanports {start|stop|restart|enable|disable}
/etc/init.d/hosts_scan {start|stop|restart|enable|disable}
```

## Configuration

The bot is configured via the UCI configuration file `/etc/config/wrtgram`.
Key options include:
*   `global.key`: Your Telegram Bot API token.
*   `global.my_chat_id`: Your Telegram Chat ID (for authorization).
*   `smtp.from` / `smtp.to`: For email alerts using `ssmtp`.

## Development Conventions

### Plugin Structure
*   **Commands:** Located in `/usr/lib/wrtgram/plugins/`. Commands can be Shell or Python (without extension).
*   **Help Files:** Every command *must* have a corresponding description file in `/usr/lib/wrtgram/plugins/help/` to be listed in the `/help` menu.
*   **Interactive Actions:** Callback scripts for inline buttons are located in `/usr/lib/wrtgram/plugins/actions/`.
*   **Internal Menus:** Interactive inline keyboards are managed directly within `sbin/bot.py`.

### Adding a New Command
1.  Create the plugin script in `usr/lib/wrtgram/plugins/`.
2.  Create the help file in `usr/lib/wrtgram/plugins/help/`.
3.  The `Makefile` automatically discovers and installs new plugins, actions, and help files.

### Shared Library
Common Python functionality (UCI reading, message sending, plugin execution) is consolidated in `/usr/lib/wrtgram/wrtgramlib.py`.
