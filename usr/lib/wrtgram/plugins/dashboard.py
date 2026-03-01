#!/usr/bin/env python3
# HELP: Display an interactive dashboard with live router stats and a refresh button.
import sys, os, subprocess, json, time, html

sys.path.append("/usr/lib/wrtgram")
import wrtapi

def format_bytes(b):
    b = float(b)
    if b < 1024:
        return f"{b:.0f} B"
    elif b < 1024 * 1024:
        return f"{b/1024:.1f} KB"
    elif b < 1024 * 1024 * 1024:
        return f"{b/(1024*1024):.1f} MB"
    else:
        return f"{b/(1024*1024*1024):.2f} GB"

def get_cpu_times():
    try:
        with open('/proc/stat', 'r') as f:
            for line in f:
                if line.startswith('cpu '):
                    return [int(x) for x in line.split()[1:]]
    except:
        pass
    return []
    
def get_wan_status():
    interfaces = ["wan", "wan_4", "ppp-wan", "wan6", "wwan"]
    # Try to find which one is active
    try:
        all_if = json.loads(subprocess.check_output(["ubus", "-t", "2", "call", "network.interface", "dump"], stderr=subprocess.DEVNULL))
        for iface in all_if.get("interface", []):
            if iface.get("up") and iface.get("interface") in interfaces:
                return iface.get("l3_device", "eth0"), iface
    except:
        pass
        
    # Fallback to checking wan specifically
    for ifname in interfaces:
        try:
            out = subprocess.check_output(["ubus", "-t", "2", "call", f"network.interface.{ifname}", "status"], stderr=subprocess.DEVNULL)
            data = json.loads(out)
            if data.get("up"):
                return data.get("l3_device", "eth0"), data
        except:
            continue
            
    return "eth0", {}

def get_wan_stats(iface):
    rx, tx = 0, 0
    try:
        with open(f"/sys/class/net/{iface}/statistics/rx_bytes", "r") as f:
            rx = int(f.read().strip())
        with open(f"/sys/class/net/{iface}/statistics/tx_bytes", "r") as f:
            tx = int(f.read().strip())
    except:
        pass
    return rx, tx

def get_temp():
    temps = []
    try:
        for z in sorted(os.listdir("/sys/class/thermal")):
            if z.startswith("thermal_zone"):
                with open(f"/sys/class/thermal/{z}/temp", "r") as f:
                    temps.append(int(f.read().strip()) / 1000.0)
    except:
        pass
    if temps:
        return f"{temps[0]:.1f}°C"
    return "N/A"
    
def make_bar(percent, length=10):
    percent = max(0, min(100, float(percent)))
    bars = int(round((percent / 100.0) * length))
    return "█" * bars + "░" * (length - bars)

def run_dashboard():
    cpu1 = get_cpu_times()
    wan_iface, wan_data = get_wan_status()
    rx1, tx1 = get_wan_stats(wan_iface)
    
    time.sleep(1)
    
    cpu2 = get_cpu_times()
    rx2, tx2 = get_wan_stats(wan_iface)
    
    # Calculate rates, handle potential counter resets
    rx_diff = rx2 - rx1 if rx2 >= rx1 else 0
    tx_diff = tx2 - tx1 if tx2 >= tx1 else 0
    
    rx_rate = format_bytes(rx_diff) + "/s"
    tx_rate = format_bytes(tx_diff) + "/s"
    
    cpu_percent = 0.0
    if cpu1 and cpu2 and len(cpu1) == len(cpu2):
        diff = [cpu2[i] - cpu1[i] for i in range(len(cpu1))]
        total = sum(diff)
        if total > 0:
            idle = diff[3]
            cpu_percent = 100.0 * (1.0 - (idle / total))
            
    try:
        sys_info = json.loads(subprocess.check_output(["ubus", "-t", "2", "call", "system", "info"]))
    except:
        sys_info = {}
        
    uptime_s = sys_info.get("uptime", 0)
    hours, remainder = divmod(int(uptime_s), 3600)
    minutes, seconds = divmod(remainder, 60)
    uptime_str = f"{hours}h {minutes}m"
    
    mem = sys_info.get("memory", {})
    total_mem = float(mem.get("total", 1))
    free_mem = float(mem.get("free", 0))
    # Buffered/Cached are often available in ubus system info too
    buffered = float(mem.get("buffered", 0))
    cached = float(mem.get("cached", 0))
    
    # "Real" used memory often excludes buffers/cache
    used_mem = total_mem - free_mem - buffered - cached
    if used_mem < 0: used_mem = total_mem - free_mem
    
    mem_percent = (used_mem * 100.0) / total_mem if total_mem > 0 else 0
    
    wan_ip = "Disconnected"
    if "ipv4-address" in wan_data and wan_data["ipv4-address"]:
        wan_ip = wan_data["ipv4-address"][0].get("address", "Disconnected")
    elif "ipv6-address" in wan_data and wan_data["ipv6-address"]:
        wan_ip = wan_data["ipv6-address"][0].get("address", "Disconnected")

    temp = get_temp()
    
    text = f"🖥 *Router Dashboard*\n"
    text += f"━━━━━━━━━━━━━━━━━━━━\n"
    text += f"🕒 *Uptime:* {uptime_str}\n"
    text += f"🔥 *CPU:* [{make_bar(cpu_percent)}] {cpu_percent:.1f}%\n"
    text += f"🧠 *RAM:* [{make_bar(mem_percent)}] {mem_percent:.1f}%\n"
    text += f"🌡 *Temp:* {temp}\n"
    text += f"🌐 *WAN IP:* {wan_ip}\n"
    text += f"⬇️ *WAN Rx:* {rx_rate} ⬆️ *Tx:* {tx_rate}\n"
    text += f"━━━━━━━━━━━━━━━━━━━━\n"
    text += f"_Last Update: {time.strftime('%H:%M:%S')}_"

    return text

if __name__ == "__main__":
    text = run_dashboard()
    keyboard = {
        "inline_keyboard": [
            [{"callback_data": "dashboard|", "text": "🔄 Refresh"}],
            [{"callback_data": "reboot|", "text": "♻️ Reboot"}]
        ]
    }
    wrtapi.tg_api_call(
        "sendMessage", 
        form_data={"chat_id": wrtapi.CHAT_ID, "parse_mode": "Markdown", "reply_markup": json.dumps(keyboard)},
        data_urlencode={"text": text}
    )
