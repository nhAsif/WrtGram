# Changelog

All notable changes to this project will be documented in this file.

---

## [2.3] - 2026-03-01

### 🐛 Bug Fixes
- **`Makefile` `prerm`:** Fixed inverted condition (`-n` → `-z` for `$IPKG_INSTROOT`). Services are now correctly stopped and disabled when running `opkg remove wrtgram` on the actual router.
- **`sbin/telegram_bot`:** Replaced all bash-specific constructs (`[[ ]]`, `==` in `[ ]`, `source`, bash string replacement) with POSIX `sh` equivalents to match the `#!/bin/sh` shebang.
- **`sbin/telegram_sender`:** Fixed `function log()` bash-ism → POSIX `log() {` syntax.
- **`sbin/telebot`:** Replaced bash string substitution `${var//_/\\_}` with POSIX `sed` for underscore escaping.
- **`sbin/lanports`:** Fixed DHCP OFFER/ACK race condition. Replaced the fragile 4-line countdown mechanism with MAC-address-based file tracking (`/tmp/wrtgram_dhcp_offer_mac`), ensuring OFFER and ACK are correctly paired even on busy networks.

### 🔐 Security
- **TLS verification enabled:** Removed `curl -k` from all scripts. All HTTPS calls now verify certificates using the system CA bundle (`/etc/ssl/certs`). A new UCI option `tls_insecure '0'` in `/etc/config/wrtgram` (set to `'1'` to revert) controls this behaviour for routers without `ca-certificates`.
- **Parameter sanitization:** Plugin arguments are now sanitized via `sed` stripping metacharacters (`"`, `&`, `;`, `<`, `>`, `|`, `\`), which is more reliable than the previous bash string substitution approach.

### 🏗️ Architecture & Reliability
- **New: `usr/lib/wrtgram/common`:** Shared library sourced by all `sbin` scripts. Eliminates duplicated UCI reads, centralises TLS configuration, provides a `tg_api_call` helper with retry and exponential backoff (up to 3 attempts, 2→4→8s delays), and a POSIX `log_msg` function.
- **Plugin execution timeout:** Each plugin in `sbin/telegram_bot` is now wrapped with `timeout 30` to prevent a hung plugin from blocking the bot indefinitely.
- **API error handling:** `sbin/telegram_bot` now sleeps 5 seconds and retries on a failed `getUpdates` call instead of spinning in a tight loop.
- **`sbin/hosts_scan`:** Replaced hardcoded `192.168.250` subnet with a dynamic lookup from `uci get network.lan.ipaddr`.

### ✨ New Plugins
- **`/bw_stats`:** Shows per-interface bandwidth statistics. Uses `vnstat` for historical data if installed (`opkg install vnstat2`), falls back to live `/proc/net/dev` counters.
- **`/version`:** Shows the installed WrtGram version and checks the GitHub API for the latest release, notifying if an update is available.

### 🔧 Plugin Improvements
- **`/status`:** Now includes disk usage (`df -h /`), WAN uptime (via `ubus`), all thermal zones (loops `/sys/class/thermal/thermal_zone*`), and active connection count (`/proc/net/nf_conntrack`).
- **`/get_ip`:** Replaced hardcoded `eth0.2` interface with dynamic WAN interface detection via `ubus` and UCI (`network.wan.device`, `network.wan.ifname`). Supports both legacy and modern `ifconfig` output formats.
- **`/lan_scan`:** Added multi-source hostname resolution: checks `/tmp/dhcp.leases`, all files under `/tmp/hosts/`, and `/etc/hosts` via a `resolve_hostname` helper.

### 🏷️ Code Quality & CI
- **`Makefile`:** Removed duplicate `TITLE:=` field. Bumped version to `2.3-1`.
- **GitHub Actions:** Added `shellcheck` CI job that lints all `sbin/` and plugin scripts before the build step. `build-openwrt` now depends on `shellcheck`. Release tag and title now use the dynamic version from `Makefile` instead of being hardcoded.

---

## [2.2] - Prior release

Initial public release. See [README.md](README.md) for full feature list.
