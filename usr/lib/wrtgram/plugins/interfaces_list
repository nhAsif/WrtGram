#!/usr/bin/env python3
"""
interfaces_list.py – Network interfaces plugin (replaces shell plugins/interfaces_list)

Calls `ubus call network.interface dump`, parses JSON natively,
and prints a formatted summary of all interfaces.
"""

import json
import subprocess
import sys


def _ubus_dump() -> dict:
    result = subprocess.run(
        ["ubus", "call", "network.interface", "dump"],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        print("Error calling ubus:", result.stderr.strip())
        sys.exit(1)
    return json.loads(result.stdout)


def _fmt_bool(val) -> str:
    return "✅ Up" if val else "❌ Down"


def main() -> None:
    data  = _ubus_dump()
    ifaces = data.get("interface", [])

    print("🔌 *Network Interfaces*\n")

    for iface in ifaces:
        name   = iface.get("interface",  "?")
        up     = iface.get("up",          False)
        device = iface.get("device",      "N/A")
        proto  = iface.get("proto",       "N/A")

        ipv4_list = iface.get("ipv4-address", [])
        ipv6_list = iface.get("ipv6-address", [])
        routes    = iface.get("route",         [])
        dns       = iface.get("dns-server",    [])

        print(f"*{name}*  {_fmt_bool(up)}")
        print(f"  Device: `{device}`  |  Proto: `{proto}`")

        for addr in ipv4_list:
            print(f"  IPv4: `{addr.get('address','?')}/{addr.get('mask','?')}`")
        for addr in ipv6_list:
            print(f"  IPv6: `{addr.get('address','?')}/{addr.get('mask','?')}`")
        for route in routes:
            src  = route.get("source",  "")
            tgt  = route.get("target",  "")
            nh   = route.get("nexthop", "")
            print(f"  Route: `{src}` → `{tgt}` via `{nh}`")
        if dns:
            print(f"  DNS: `{'  '.join(dns)}`")

        print()  # blank line between interfaces


if __name__ == "__main__":
    main()
