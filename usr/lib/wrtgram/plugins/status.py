#!/usr/bin/env python3
# HELP: Shows the router status, including uptime, CPU load, RAM usage, and CPU temperature.
import sys, os, subprocess, json, time, math

sys.path.append("/usr/lib/wrtgram")
import wrtapi

def format_uptime(seconds):
    try:
        seconds = int(seconds)
        days, remainder = divmod(seconds, 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        parts = []
        if days > 0: parts.append(f"{days}d")
        if hours > 0: parts.append(f"{hours}h")
        parts.append(f"{minutes}m")
        return " ".join(parts)
    except:
        return "N/A"

def get_sys_info():
    try:
        out = subprocess.check_output(["ubus", "-t", "2", "call", "system", "info"], stderr=subprocess.DEVNULL)
        return json.loads(out)
    except:
        return {}

def get_disk_info():
    try:
        out = subprocess.check_output(["df", "-h", "/"], stderr=subprocess.DEVNULL).decode('utf-8')
        lines = out.strip().split('\n')
        if len(lines) > 1:
            parts = lines[1].split()
            if len(parts) >= 5:
                return parts[2], parts[3], parts[4] # used, avail, percent
    except:
        pass
    return "N/A", "N/A", "N/A"

def get_wan_uptime():
    try:
        # Try finding any active WAN
        interfaces = ["wan", "wan_4", "ppp-wan", "wan6"]
        for ifname in interfaces:
            try:
                out = subprocess.check_output(["ubus", "-t", "2", "call", f"network.interface.{ifname}", "status"], stderr=subprocess.DEVNULL)
                data = json.loads(out)
                if data.get("up") and data.get("uptime"):
                    return format_uptime(data.get("uptime"))
            except:
                continue
    except:
        pass
    return "N/A"

def get_temps():
    temps = []
    try:
        for z in sorted(os.listdir("/sys/class/thermal")):
            if z.startswith("thermal_zone"):
                try:
                    with open(f"/sys/class/thermal/{z}/temp", "r") as f:
                        t = int(f.read().strip()) / 1000.0
                        temps.append(f"🌡 *Temp ({z}):* {t:.1f}°C")
                except: continue
    except:
        pass
    if temps:
        return "\n".join(temps)
    return "🌡 *CPU Temp:* N/A"

def get_active_connections():
    try:
        if os.path.exists("/proc/net/nf_conntrack"):
            out = subprocess.check_output(["wc", "-l", "/proc/net/nf_conntrack"], stderr=subprocess.DEVNULL).decode('utf-8')
            return out.split()[0]
        elif os.path.exists("/proc/net/ip_conntrack"):
            out = subprocess.check_output(["wc", "-l", "/proc/net/ip_conntrack"], stderr=subprocess.DEVNULL).decode('utf-8')
            return out.split()[0]
    except:
        pass
    return "N/A"

if __name__ == "__main__":
    sys_info = get_sys_info()
    
    uptime_raw = sys_info.get("uptime", 0)
    uptime_str = format_uptime(uptime_raw)
    
    load_arr = sys_info.get("load", [0, 0, 0])
    load_avg = ", ".join([f"{float(l)/65536.0:.2f}" for l in load_arr])
    
    mem = sys_info.get("memory", {})
    total_mem = float(mem.get("total", 1))
    free_mem = float(mem.get("free", 0))
    used_mem = total_mem - free_mem
    mem_percent = (used_mem * 100.0) / total_mem if total_mem > 0 else 0
    
    disk_used, disk_avail, disk_pct = get_disk_info()
    wan_uptime = get_wan_uptime()
    temp_str = get_temps()
    conn_count = get_active_connections()

    text = f"📊 *Router Status*\n\n"
    text += f"🕒 *Uptime:* {uptime_str}\n"
    text += f"🌐 *WAN Uptime:* {wan_uptime}\n"
    text += f"⚙️ *CPU Load:* {load_avg}\n"
    text += f"🧠 *RAM:* {mem_percent:.1f}% used\n"
    text += f"💾 *Disk /:* {disk_used} used, {disk_avail} free ({disk_pct})\n"
    text += f"🔗 *Connections:* {conn_count}\n\n"
    text += f"{temp_str}"

    wrtapi.tg_api_call(
        "sendMessage", 
        form_data={"chat_id": wrtapi.CHAT_ID, "parse_mode": "Markdown"},
        data_urlencode={"text": text}
    )
