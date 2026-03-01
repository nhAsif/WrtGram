# WrtGram

![ShellCheck](https://github.com/nhAsif/WrtGram/actions/workflows/simple-build-release.yml/badge.svg)

A set of scripts to manage and monitor an OpenWrt router through Telegram.

WrtGram provides a simple yet powerful way to interact with your OpenWrt router using a Telegram bot. It features a lightweight, extensible plugin architecture, allowing you to easily add new commands and features.

## Features

*   **Telegram Bot Integration:** Control your OpenWrt router using simple Telegram commands.
*   **Extensible Plugin Architecture:** Easily add new functionality by creating simple shell scripts.
*   **System Monitoring:** Get notified about LAN port status changes, DHCP leases, and more.
*   **UCI Compliant:** Uses the standard OpenWrt Unified Configuration Interface (UCI) for configuration.
*   **Rich Command Set:** Comes with a wide range of pre-built commands for common administrative tasks.
*   **New User Connection Notification:** Sends a notification to the bot when a new user connects to the network.

## How it Works

The core of the project is a daemon script that polls the Telegram API for new messages. When a command is received from an authorized user, the script executes a corresponding plugin from the `/usr/lib/wrtgram/plugins/` directory. The output of the plugin is then sent back to the user as the response.

## Getting Started

### Prerequisites

*   An OpenWrt router.
*   A Telegram account.

### Installation and Configuration

1.  **Create a Telegram Bot:**
    Follow the official instructions to create a new bot and obtain your API token: [https://core.telegram.org/bots#creating-a-new-bot](https://core.telegram.org/bots#creating-a-new-bot)

2.  **Get your Chat ID:**
    After creating the bot, send a message to it from your Telegram account. Then, run the following command on your router, replacing `<YOUR BOT TOKEN>` with the token you just obtained:

    ```bash
    curl -s -k -X GET https://api.telegram.org/bot<YOUR BOT TOKEN>/getUpdates | grep -oE '"id":[[:digit:]]+' | head -n1 | awk -F : '{print $2}'
    ```

    This will return your unique Chat ID.

3.  **Configure the Bot:**
    Open the configuration file `/etc/config/wrtgram` and set the following options:

    ```
    config wrtgram 'global'
        option key '<YOUR BOT TOKEN>'
        option my_chat_id '<YOUR CHAT ID>'
        option tls_insecure '0'   # Set to '1' only if ca-certificates is not installed
    ```

4.  **Enable and Start the Services:**
    Run the following commands to enable and start the necessary services:

    ```bash
    /etc/init.d/lanports enable && /etc/init.d/telegram_bot enable
    /etc/init.d/lanports start && /etc/init.d/telegram_bot start
    ```

Your bot should now be running and ready to accept commands.

## Plugins

Plugins are simple shell scripts located in the `/usr/lib/wrtgram/plugins/` directory. The name of the script corresponds to the command you send to the bot (e.g., the `get_ip` script is executed by the `/get_ip` command).

### Included Commands

The following commands are included by default:

*   `/bw_stats`: Shows per-interface bandwidth stats (RX/TX). Uses `vnstat` if installed, otherwise reads `/proc/net/dev`.
*   `/cf_tunnel [port]`: Creates a temporary Cloudflare tunnel to a specified port (defaults to 80).
*   `/cf_tunnel_stop`: Stops the running Cloudflare tunnel.
*   `/fw_add <hostname> [time]`: Blocks a hostname in the firewall. Can be time-based.
*   `/fw_delete [hostname]`: Removes a firewall rule for a hostname.
*   `/fw_disable`: Disables a firewall rule.
*   `/fw_enable`: Enables a firewall rule.
*   `/fw_list`: Lists all firewall rules.
*   `/fw_unblock`: Removes a block rule for a hostname.
*   `/fwr_disable`: Disables a redirect firewall rule.
*   `/fwr_enable`: Enables a redirect firewall rule.
*   `/fwr_list`: Lists all redirect firewall rules.
*   `/get_ip`: Gets the WAN IP address (dynamically detects the WAN interface).
*   `/get_mac <mac_address>`: Gets the vendor of a MAC address.
*   `/get_ping <host>`: Pings a host to check its status.
*   `/get_uptime`: Shows the router's uptime.
*   `/hst_list [hostname]`: Lists DHCP leases, optionally filtering by hostname.
*   `/ignoredmac_add <mac_address>`: Adds a MAC address to the ignore list for new connection notifications.
*   `/ignoredmac_list`: Lists ignored MAC addresses.
*   `/interface_down <interface>`: Shuts down a network interface.
*   `/interface_restart <interface>`: Restarts a network interface.
*   `/interface_up <interface>`: Starts up a network interface.
*   `/interfaces_list`: Lists all network interfaces and their status.
*   `/lan_scan`: Scans the LAN for active and inactive devices and shows their IP and MAC addresses.
*   `/netstat`: Shows network connections.
*   `/opkg_install <package>`: Installs an OpenWrt package.
*   `/opkg_update`: Updates the list of available packages.
*   `/proc_list`: Lists running processes.
*   `/proc_restart <service>`: Restarts a service.
*   `/proc_start <service>`: Starts a service.
*   `/proc_stop <service>`: Stops a service.
*   `/reboot`: Reboots the router.
*   `/start`: Shows the main help menu with all commands.
*   `/status`: Shows router status including uptime, WAN uptime, CPU load, RAM usage, disk usage, temperature (all zones), and active connections.
*   `/swports_list`: Lists the status of all switch ports.
*   `/tmate`: Creates a new tmate session for remote access.
*   `/version`: Shows the installed WrtGram version and checks GitHub for updates.
*   `/wifi_disable <device>`: Disables a Wi-Fi radio.
*   `/wifi_enable <device>`: Enables a Wi-Fi radio.
*   `/wifi_list`: Lists all Wi-Fi devices.
*   `/wifi_restart <device>`: Restarts a Wi-Fi radio.
*   `/wll_list`: Lists connected Wi-Fi clients.


### Creating Your Own Plugins

To add a new command, create a shell script in `/usr/lib/wrtgram/plugins/`. The script name maps directly to the Telegram command (e.g., `mycommand` → `/mycommand`). Output is sent back to the user.

You can source the shared library for convenient API helpers:

```sh
#!/bin/sh
. /usr/lib/wrtgram/common  # provides WRTGRAM_API, CURL_TLS, tg_send, tg_api_call

echo "Hello from myplugin!"
```

Add a help file with the same name in `/usr/lib/wrtgram/plugins/help/`. See [plugins_README.md](plugins_README.md) for a full step-by-step guide.

### Ignored MAC Addresses

The file `/etc/wrtgram/macaddr.ignore` contains MAC addresses that should be excluded from new-device connection notifications (one per line, lowercase, colon-separated):

```
aa:bb:cc:dd:ee:ff
11:22:33:44:55:66
```

Use `/ignoredmac_add <mac>` or edit the file directly.

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