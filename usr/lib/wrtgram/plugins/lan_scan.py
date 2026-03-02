#!/usr/bin/env python3
"""
lan_scan.py – Async LAN scan plugin (replaces shell plugins/lan_scan)

Parallel-pings the full /24 subnet, cross-references /tmp/dhcp.leases
and /proc/net/arp, then prints active and inactive hosts.
"""

import asyncio
import subprocess
import sys


def _get_lan_prefix() -> str:
    r = subprocess.run(
        ["uci", "get", "network.lan.ipaddr"],
        capture_output=True, text=True,
    )
    ip = r.stdout.strip()
    if not ip:
        print("Could not determine LAN IP.")
        sys.exit(1)
    return ".".join(ip.split(".")[:3])


def _read_leases() -> dict[str, tuple[str, str]]:
    """Return {ip: (mac, hostname)} from /tmp/dhcp.leases."""
    leases: dict[str, tuple[str, str]] = {}
    try:
        with open("/tmp/dhcp.leases") as f:
            for line in f:
                parts = line.split()
                if len(parts) >= 4:
                    _, mac, ip, hostname = parts[0], parts[1], parts[2], parts[3]
                    leases[ip] = (mac.upper(), hostname if hostname != "*" else "Unknown")
    except FileNotFoundError:
        pass
    return leases


def _read_arp() -> dict[str, str]:
    """Return {ip: mac} from /proc/net/arp."""
    arp: dict[str, str] = {}
    try:
        with open("/proc/net/arp") as f:
            next(f)  # header
            for line in f:
                parts = line.split()
                if len(parts) >= 4 and parts[3] != "00:00:00:00:00:00":
                    arp[parts[0]] = parts[3].upper()
    except Exception:
        pass
    return arp


async def _ping(ip: str) -> bool:
    proc = await asyncio.create_subprocess_exec(
        "ping", "-c", "1", "-w", "1", ip,
        stdout=asyncio.subprocess.DEVNULL,
        stderr=asyncio.subprocess.DEVNULL,
    )
    await proc.wait()
    return proc.returncode == 0


async def _scan_all(prefix: str) -> set[str]:
    """Ping all .1–.254 addresses in parallel, return set of live IPs."""
    results = await asyncio.gather(
        *[_ping(f"{prefix}.{i}") for i in range(1, 255)]
    )
    return {f"{prefix}.{i}" for i, up in enumerate(results, 1) if up}


async def main_async() -> None:
    prefix = _get_lan_prefix()
    leases = _read_leases()
    arp    = _read_arp()

    print("🌐 *LAN Device Status*")
    print("_Scanning the LAN… (this may take a moment)_\n")

    alive = await _scan_all(prefix)

    # ── Active hosts ─────────────────────────────────────────────────────
    print("🟢 *Active Hosts*")
    if alive:
        for ip in sorted(alive, key=lambda x: [int(n) for n in x.split(".")]):
            hostname = leases.get(ip, (arp.get(ip, "N/A"), "Unknown"))[1]
            mac      = arp.get(ip) or leases.get(ip, ("N/A",))[0]
            print(f"  🟢 *{hostname}*  `{ip}`  `{mac}`")
    else:
        print("  _No active hosts responded to ping._")

    print()

    # ── Inactive hosts (have a lease but didn't respond) ─────────────────
    print("🔴 *Inactive Hosts (from DHCP leases)*")
    inactive = [ip for ip in leases if ip not in alive]
    if inactive:
        for ip in sorted(inactive, key=lambda x: [int(n) for n in x.split(".")]):
            hostname = leases[ip][1]
            mac      = leases[ip][0]
            print(f"  🔴 *{hostname}*  `{ip}`  `{mac}`")
    else:
        print("  _All hosts with DHCP leases are currently active._")


def main() -> None:
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
