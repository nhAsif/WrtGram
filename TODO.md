# WrtGram Refactoring & Feature To-Do List

This document tracks the progress of migrating WrtGram from shell scripts to Python and introducing advanced features.

## ✅ Phase 1: Reorganizing and Standardizing Python Environment (COMPLETED)
- [x] Create a centralized Python core module (`usr/lib/wrtgram/wrtapi.py`).
- [x] Refactor core daemons (`telegram_bot`, `telegram_sender`, `telebot`) to use `wrtapi.py`.
- [x] Add Python-native plugin support (`telegram_bot` dynamically executes `.py` plugins if found).
- [x] Fix OpenWrt `init.d` script evaluating Python as Shell.
- [x] Fix GitHub Actions v4 `git` backwards compatibility crashes.
- [x] Bump `Makefile` version to `2.4.0`.

## ✅ Phase 2: Rewriting Background Daemons in Python (COMPLETED)
- [x] **Rewrite `hosts_scan` (ARP/Ping Scanner)**: 
  - Convert `sbin/hosts_scan` to Python.
  - Implement asynchronous parallel pinging for drastically faster scanning.
  - Cross-reference MAC addresses with an offline OUI database to detect device brands (e.g., "Apple iPhone").
- [x] **Rewrite `lanports` (Log Monitor)**: 
  - Convert `sbin/lanports` to Python.
  - Directly tail system logs (`syslog`), maintaining better state to detect DHCP lease assignments and Switch Port state changes instantly.

## ⏳ Phase 3: Upgrading Core Commands (Python Ports)
- [x] **`/dashboard` & `/status`**: 
  - Rewrite in Python to use direct `ubus` calls.
  - Add unicode progress bars for memory/CPU (e.g., `[██████░░░░] 60%`).
  - Read active bandwidth consumption metrics.
- [ ] **`/fw_list` & `/start`**: 
  - Rewrite the inline keyboard context generator (`usr/lib/wrtgram/plugins/ctx`).
  - Introduce an interactive "Pagination" system for handling 50+ list items across multiple menu pages.

## ✅ Phase 4: Brand New Advanced Features (COMPLETED)
- [x] **Command Aliases & Shortcuts**: 
  - Allow users to map custom commands (e.g., `/ip` -> `/get_ip`).
- [x] **Interactive Menus (Conversations)**: 
  - Implement sequential state for commands (e.g., `/fw_add` -> Box asks for IP -> Box asks for Time -> Complete).

## ⏳ Phase 5: Build System & Repo Cleanup
- [ ] Merge tiny `plugins/help/` text files into Python `docstrings` or comments to reduce disk I/O.
- [ ] Create a post-install migration script to gracefully prune deprecated shell files from legacy installations.
