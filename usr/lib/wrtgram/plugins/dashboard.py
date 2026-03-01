#!/usr/bin/env python3
import sys, os, subprocess, json, time

sys.path.append("/usr/lib/wrtgram")
import wrtapi

def format_bytes(b):
    if b < 1024:
        return f"{b} B"
    elif b < 1024 * 1024:
        return f"{b/1024:.1f} KB"
    else:
        return f"{b/(1024*1024):.1f} MB"

def get_cpu_times():
    try:
        with open('/proc/stat', 'r') as f:
            for line in f:
                if line.startswith('cpu '):
                    return [int(x) for x in line.split()[1:]]
    except:
        pass
    return []
    
def get_wan_iface():
    try:
        out = subprocess.check_output(["ubus", "call", "network.interface.wan", "status"], stderr=subprocess.DEVNULL)
        data = json.loads(out)
        return data.get("l3_device", "eth0"), data
    except:
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
        for z in os.listdir("/sys/class/thermal"):
            if z.startswith("thermal_zone"):
                with open(f"/sys/class/thermal/{z}/temp", "r") as f:
                    temps.append(int(f.read().strip()) / 1000.0)
    except:
        pass
    if temps:
        return f"{temps[0]:.1f}°C"
    return "N/A"
    
def make_bar(percent, length=10):
    bars = int(round((percent / 100.0) * length))
    if bars > length: bars = length
    if bars < 0: bars = 0
    return "█" * bars + "░" * (length - bars)

def run_dashboard():
    cpu1 = get_cpu_times()
    wan_iface, wan_data = get_wan_iface()
    rx1, tx1 = get_wan_stats(wan_iface)
    
    time.sleep(1)
    
    cpu2 = get_cpu_times()
    rx2, tx2 = get_wan_stats(wan_iface)
    
    rx_rate = format_bytes(rx2 - rx1) + "/s"
    tx_rate = format_bytes(tx2 - tx1) + "/s"
    
    cpu_percent = 0.0
    if cpu1 and cpu2 and len(cpu1) == len(cpu2):
        diff = [cpu2[i] - cpu1[i] for i in range(len(cpu1))]
        total = sum(diff)
        if total > 0:
            idle = diff[3]
            cpu_percent = 100.0 * (1.0 - (idle / total))
            
    try:
        sys_info = json.loads(subprocess.check_output(["ubus", "call", "system", "info"]))
    except:
        sys_info = {}
        
    uptime_s = sys_info.get("uptime", 0)
    hours, remainder = divmod(uptime_s, 3600)
    minutes, seconds = divmod(remainder, 60)
    uptime_str = f"{int(hours)}h {int(minutes)}m"
    
    mem = sys_info.get("memory", {})
    total_mem = mem.get("total", 1)
    free_mem = mem.get("free", 0)
    used_mem = total_mem - free_mem
    mem_percent = (used_mem * 100.0) / total_mem if total_mem > 0 else 0
    
    wan_ip = "Disconnected"
    if "ipv4-address" in wan_data and wan_data["ipv4-address"]:
        wan_ip = wan_data["ipv4-address"][0].get("address", "Disconnected")

    temp = get_temp()
    
    text = f'''🖥️ *Router Dashboard*
━━━━━━━━━━━━━━━━━━━━
🕒 *Uptime:* {uptime_str}
🔥 *CPU:* [{make_bar(cpu_percent)}] {cpu_percent:.1f}%
🧠 *RAM:* [{make_bar(mem_percent)}] {mem_percent:.1f}%
🌡️ *Temp:* {temp}
🌐 *WAN IP:* {wan_ip}
⬇️ *WAN Rx:* {rx_rate} ⬆️ *Tx:* {tx_rate}
━━━━━━━━━━━━━━━━━━━━
_Last Update: {time.strftime('%H:%M:%S')}_'''

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
