# How to Add New Plugins to WrtGram

This document provides a guide on how to extend the functionality of the `wrtgram` project by adding new command plugins. This is crucial for future AI tools to understand the project's extensibility.

## Plugin Architecture Overview

The WrtGram bot operates on a simple, yet powerful, plugin architecture:

*   **Main Bot Script (`sbin/telegram_bot`):** This script continuously polls Telegram for new messages. When an authorized user sends a command (e.g., `/mycommand`), the bot looks for a corresponding script in the plugins directory.
*   **Plugins Directory (`usr/lib/wrtgram/plugins/`):** This is where the main script for each bot command resides. The filename (without extension or path) directly corresponds to the Telegram command. The standard output of these scripts is sent back to the user as the command's response.
*   **Action Scripts (`usr/lib/wrtgram/plugins/actions/`):** These scripts are executed in response to inline keyboard button presses, typically after a "context" script has presented options to the user.
*   **Context Scripts (`usr/lib/wrtgram/plugins/ctx/`):** These scripts are used for commands that require user interaction. They display options (e.g., via inline keyboards) and set up the context for subsequent "action" scripts.
*   **Help Files (`usr/lib/wrtgram/plugins/help/`):** These are plain text files with the same name as a plugin. Their content is displayed when the user runs the `/start` command, providing built-in help for each command.
*   **OpenWrt Makefile:** The project is packaged as an OpenWrt IPK. The `Makefile` defines which files are included in the final package and where they are installed on the router. Any new plugin files *must* be added to the `Makefile` to be deployed.

## Step-by-Step Guide to Adding a New Plugin

To add a new command plugin (e.g., `/mycommand`), follow these steps:

### 1. Create the Main Plugin Script

1.  **Create a new shell script file:** `usr/lib/wrtgram/plugins/mycommand` (replace `mycommand` with your desired command name).
2.  **Add your script logic:** Write the shell commands that perform the desired action. Any output printed to `stdout` by this script will be sent back to the user in Telegram.
    *   Example:
        ```bash
        #!/bin/sh
        # mycommand plugin
        echo "Hello from mycommand!"
        # You can use UCI commands, other shell utilities, etc.
        # uci get wireless.@wifi-iface[0].ssid
        ```
3.  **Make the script executable:** Ensure the script has execute permissions (`chmod +x usr/lib/wrtgram/plugins/mycommand`). This is handled by `INSTALL_BIN` in the Makefile, but good practice for local testing.

### 2. Create the Help File

1.  **Create a new plain text file:** `usr/lib/wrtgram/plugins/help/mycommand` (again, `mycommand` should match your plugin name).
2.  **Add a brief description:** Write a concise explanation of what your command does. This text will appear when the user sends the `/start` command to the bot.
    *   Example:
        ```
        This command greets the user.
        ```

### 3. (Optional) Create Interactive Context and Action Scripts

If your command requires user interaction (e.g., selecting from a list of options using inline keyboard buttons):

1.  **Create a Context Script:** `usr/lib/wrtgram/plugins/ctx/mycommand_ctx`. This script will generate the inline keyboard options.
2.  **Create one or more Action Scripts:** `usr/lib/wrtgram/plugins/actions/mycommand_action1`, `usr/lib/wrtgram/plugins/actions/mycommand_action2`, etc. These scripts will be executed when the user taps an inline keyboard button.

### 4. Update the OpenWrt `Makefile`

This is a **critical step** to ensure your new files are included in the OpenWrt package.

1.  **Edit the `Makefile`** located in the project root.
2.  **Locate the `define Package/wrtgram/install` section.**
3.  **Add your new plugin script:** Find the `$(INSTALL_BIN)` block for `$(1)/usr/lib/wrtgram/plugins` and add an entry for `./usr/lib/wrtgram/plugins/mycommand`.
    *   Example snippet from `Makefile`:
        ```makefile
        	$(INSTALL_DIR) $(1)/usr/lib/wrtgram/plugins
        	$(INSTALL_BIN) ...existing_plugins... \
        			./usr/lib/wrtgram/plugins/mycommand \
        			...more_existing_plugins... \
        		$(1)/usr/lib/wrtgram/plugins
        ```
4.  **Add your new help file:** Find the `$(INSTALL_DATA)` block for `$(1)/usr/lib/wrtgram/plugins/help` and add an entry for `./usr/lib/wrtgram/plugins/help/mycommand`.
    *   Example snippet from `Makefile`:
        ```makefile
        	$(INSTALL_DIR) $(1)/usr/lib/wrtgram/plugins/help
        	$(INSTALL_DATA) ...existing_help_files... \
        			./usr/lib/wrtgram/plugins/help/mycommand \
        			...more_existing_help_files... \
        		$(1)/usr/lib/wrtgram/plugins/help
        ```
5.  **(If applicable) Add context and action scripts:** Similarly, add entries for any `ctx` or `actions` scripts you created to their respective `$(INSTALL_BIN)` blocks in the `Makefile`.

### 5. Rebuild and Reinstall the Package

After making changes to the `Makefile` or adding new files, you need to rebuild the OpenWrt package and reinstall it on your router:

1.  **Rebuild:** Execute the OpenWrt build process to generate a new `.ipk` package. (This typically involves running `make package/wrtgram/compile` or `make V=s` from your OpenWrt SDK/buildroot).
2.  **Transfer:** Copy the newly generated `.ipk` file to your OpenWrt router (e.g., using `scp`).
3.  **Reinstall:** On your OpenWrt router, uninstall the old package and install the new one:
    ```bash
    opkg remove wrtgram
    opkg install /path/to/your/new_wrtgram.ipk
    ```
    The `postinst` script defined in the `Makefile` will automatically restart the necessary services.

Once these steps are completed, your new command `/mycommand` should be available through your Telegram bot and listed in the `/start` menu.
