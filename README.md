# WrtGram

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

*   `/cf_tunnel [port]`: Creates a temporary Cloudflare tunnel.
*   `/cf_tunnel_stop`: Stops the running Cloudflare tunnel.
*   `/fw_add <hostname> [time]`: Block a hostname in the firewall.
*   `/fw_delete [hostname]`: Remove a firewall rule.
*   `/fw_disable`: Disable a firewall rule.
*   `/fw_enable`: Enable a firewall rule.
*   `/fw_list`: List all firewall rules.
*   `/fw_unblock`: Remove a hostname from a deny firewall rule.
*   `/fwr_disable`: Disable a redirect firewall rule.
*   `/fwr_enable`: Enable a redirect firewall rule.
*   `/fwr_list`: List all redirect firewall rules.
*   `/get_ip`: Get the WAN IP address.
*   `/get_mac <mac_address>`: Get the vendor of a MAC address.
*   `/get_ping <host>`: Ping a host to check its status.
*   `/get_uptime`: Show the router's uptime.
*   `/hst_list [hostname]`: List DHCP leases.
*   `/ignoredmac_add <mac_address>`: Add a MAC address to the ignore list.
*   `/ignoredmac_list`: List ignored MAC addresses.
*   `/interface_down <interface>`: Shut down an interface.
*   `/interface_restart <interface>`: Restart an interface.
*   `/interface_up <interface>`: Start up an interface.
*   `/interfaces_list`: List all network interfaces.
*   `/netstat`: Show network connections.
*   `/opkg_install <package>`: Install a package.
*   `/opkg_update`: Update the package list.
*   `/proc_list`: List running processes.
*   `/proc_restart <process>`: Restart a service.
*   `/proc_start <process>`: Start a service.
*   `/proc_stop <process>`: Stop a service.
*   `/reboot`: Reboot the router.
*   `/start`: Show the help menu.
*   `/swports_list`: List switch port status.
*   `/tmate`: Create a new tmate session for remote access.
*   `/wifi_disable <device>`: Disable a Wi-Fi radio.
*   `/wifi_enable <device>`: Enable a Wi-Fi radio.
*   `/wifi_list`: List all Wi-Fi devices.
*   `/wifi_restart <device>`: Restart a Wi-Fi radio.
*   `/wll_list`: List connected Wi-Fi clients.

### Creating Your Own Plugins

To add a new command, simply create a new shell script in the `/usr/lib/wrtgram/plugins/` directory. The script can contain any valid OpenWrt shell commands. Any output from the script will be sent back to the user as a message.

You can also add a help file for your command in the `/usr/lib/wrtgram/plugins/help/` directory. The name of the help file should be the same as your command's name.

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

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.