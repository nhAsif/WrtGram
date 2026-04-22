# WrtGram

A set of scripts to manage and monitor an OpenWrt router through Telegram, now rewritten in Python for improved performance and features.

WrtGram provides a simple yet powerful way to interact with your OpenWrt router using a Telegram bot. It features a lightweight, extensible plugin architecture, allowing you to easily add new commands and features using either Python or Shell scripts.

## Features

*   **Asynchronous Python Bot:** Built with `python-telegram-bot` (v20+) for high-performance, non-blocking interaction.
*   **🤖 AI Assistant (Powered by OpenRouter):** Integrated LLM that can answer questions, execute shell commands, and even write new plugins dynamically.
*   **Extensible Plugin Architecture:** Easily add new functionality by creating simple shell or Python scripts.
*   **Interactive Inline Keyboards:** Direct router control through native Telegram buttons (no more external context scripts).
*   **System Monitoring:** Get notified about LAN port status changes, DHCP leases, and more via async background daemons.
*   **UCI Compliant:** Uses the standard OpenWrt Unified Configuration Interface (UCI) for configuration.
*   **Rich Command Set:** Comes with a wide range of pre-built commands for common administrative tasks, including a richer `/status` view.
*   **New User Connection Notification:** Sends a notification to the bot when a new user connects to the network.

## How it Works

The core of the project consists of three Python-based background services:
1.  `telegram_bot`: The main async daemon that listens for Telegram messages and executes plugins.
2.  `lanports`: An async log monitor that watches for LAN and DHCP events.
3.  `hosts_scan`: A parallelized scanner that identifies new hosts on the network.

When a command is received from an authorized user, the bot executes a corresponding plugin from the `/usr/lib/wrtgram/plugins/` directory.

## Getting Started

### Prerequisites

*   An OpenWrt router with Python 3 installed.
*   A Telegram account.
*   The `python-telegram-bot` library.

### Installation and Configuration

1.  **Create a Telegram Bot:**
    Follow the official instructions to create a new bot and obtain your API token: [https://core.telegram.org/bots#creating-a-new-bot](https://core.telegram.org/bots#creating-a-new-bot)

2.  **Get your Chat ID:**
    After creating the bot, send a message to it from your Telegram account. Then, run the following command on your router, replacing `<YOUR BOT TOKEN>` with the token you just obtained:

    ```bash
    curl -s -k -X GET https://api.telegram.org/bot<YOUR BOT TOKEN>/getUpdates | grep -oE '"id":[[:digit:]]+' | head -n1 | awk -F : '{print $2}'
    ```

3.  **Install Dependencies:**
    Ensure Python 3 is installed and then install the required Telegram library:

    ```bash
    opkg update && opkg install python3-pip
    pip3 install python-telegram-bot
    ```

4.  **Configure the Bot:**
    Open the configuration file `/etc/config/wrtgram` and set your token and chat ID:

    ```
    config wrtgram 'global'
        option key '<YOUR BOT TOKEN>'
        option my_chat_id '<YOUR CHAT ID>'
        option openrouter_key '<YOUR OPENROUTER API KEY>'
        option openrouter_model 'meta-llama/llama-3.1-8b-instruct:free'
    ```

    *Note: You can get an API key from [OpenRouter.ai](https://openrouter.ai/).*

5.  **Enable and Start the Services:**
    Run the following commands to enable and start the services:

    ```bash
    /etc/init.d/lanports enable && /etc/init.d/hosts_scan enable && /etc/init.d/telegram_bot enable
    /etc/init.d/lanports start && /etc/init.d/hosts_scan start && /etc/init.d/telegram_bot start
    ```

Your bot should now be running and ready to accept commands.

## Plugins

Plugins are scripts located in the `/usr/lib/wrtgram/plugins/` directory. Both Shell scripts (no extension) and Python scripts (`.py` extension) are supported.

### Included Commands

The following commands are included by default:

*   `/ai <prompt>`: Ask the AI assistant to help you with information, execute tasks, or even write new plugins.
*   `/cf_tunnel [port]`: Creates a temporary Cloudflare tunnel (defaults to 80).
*   `/cf_tunnel_stop`: Stops the running Cloudflare tunnel.
*   `/fw_add <hostname> [time]`: Blocks a hostname in the firewall.
*   `/fw_delete [hostname]`: Removes a firewall rule for a hostname.
*   `/fw_disable`: Disables a firewall rule.
*   `/fw_enable`: Enables a firewall rule.
*   `/fw_list`: Lists all firewall rules (structured output).
*   `/fw_unblock`: Removes a block rule for a hostname.
*   `/fwr_disable`: Disables a redirect firewall rule.
*   `/fwr_enable`: Enables a redirect firewall rule.
*   `/fwr_list`: Lists all redirect firewall rules.
*   `/get_ip`: Gets the WAN IP address.
*   `/get_mac <mac_address>`: Gets the vendor of a MAC address.
*   `/get_ping <host>`: Pings a host.
*   `/get_uptime`: Shows the router's uptime.
*   `/help`: Lists all available commands with their descriptions.
*   `/hst_list [hostname]`: Lists DHCP leases.
*   `/ignoredmac_add <mac_address>`: Adds a MAC address to the notification ignore list.
*   `/ignoredmac_list`: Lists ignored MAC addresses.
*   `/interface_down <interface>`: Shuts down a network interface.
*   `/interface_restart <interface>`: Restarts a network interface.
*   `/interface_up <interface>`: Starts up a network interface.
*   `/interfaces_list`: Lists all network interfaces and their status (parsed from ubus JSON).
*   `/lan_scan`: Scans the LAN for active devices (using async parallel scanning).
*   `/netstat`: Shows network connections.
*   `/opkg_install <package>`: Installs an OpenWrt package.
*   `/opkg_update`: Updates the package list.
*   `/proc_list`: Lists running processes.
*   `/proc_restart <service>`: Restarts a service.
*   `/proc_start <service>`: Starts a service.
*   `/proc_stop <service>`: Stops a service.
*   `/reboot`: Reboots the router.
*   `/start`: Shows the welcome message.
*   `/status`: Shows rich router status with uptime, CPU load, and RAM usage bar.
*   `/swports_list`: Lists the status of switch ports.
*   `/tmate`: Creates a new tmate session for remote access.
*   `/wifi_disable <device>`: Disables a Wi-Fi radio.
*   `/wifi_enable <device>`: Enables a Wi-Fi radio.
*   `/wifi_list`: Lists all Wi-Fi devices with signal data.
*   `/wifi_restart <device>`: Restarts a Wi-Fi radio.
*   `/wll_list`: Lists connected Wi-Fi clients.

### Creating Your Own Plugins

To add a new command, create a new Shell or Python script in `/usr/lib/wrtgram/plugins/`.
-   **Shell Plugins:** Use standard script naming (e.g., `my_cmd`).
-   **Python Plugins:** End with `.py` (e.g., `my_cmd.py`).

The bot automatically identifies these and adds them to the `/help` list if a corresponding help file exists in `/usr/lib/wrtgram/plugins/help/`.

## Services

This project includes the following services that run in the background:

*   `telegram_bot`: The main bot daemon that listens for and executes commands.
*   `lanports`: Monitors the router's logs and sends notifications for LAN port status changes and DHCP leases.
*   `hosts_scan`: Scans the network for new hosts and sends notifications.

## Troubleshooting

If the bot is not responding, check the following:

*   Ensure that the `telegram_bot` service is running: `ps | grep telegram_bot`
*   Check the system log for any errors: `logread | grep telegram_bot`
*   Make sure your bot token and chat ID are correct in `/etc/config/wrtgram`.

## Contributing

Contributions are welcome! Please see the [CONTRIBUTING.md](CONTRIBUTING.md) file for guidelines.

## Credits

This project is based on the original telegramopenwrt by [alexwbaule](https://github.com/alexwbaule/telegramopenwrt).

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.