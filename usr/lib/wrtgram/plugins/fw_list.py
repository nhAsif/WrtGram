#!/usr/bin/env python3
import sys, os, subprocess

sys.path.append("/usr/lib/wrtgram")
import wrtapi

def run_fw_list():
    text = "🛡️ *Firewall Rules*\n━━━━━━━━━━━━━━\n"
    try:
        out = subprocess.check_output(["uci", "-q", "show", "firewall"], stderr=subprocess.DEVNULL).decode('utf-8')
        rules = []
        current_rule = {}
        
        # A simple parser for uci show firewall
        for line in out.splitlines():
            if ".@rule[" in line:
                idx = line.split('[')[1].split(']')[0]
                attr = line.split('].')[1].split('=')[0]
                val = line.split('=')[1].strip("'")
                
                # We can group by index if we wanted to be very precise, 
                # but for listing names we can just find .name
                if attr == "name":
                    name = val
                    enabled = wrtapi.get_uci(f"firewall.@rule[{idx}].enabled", "1")
                    status = "✅" if enabled == "1" else "❌"
                    text += f"{status} *{name}* (ID: {idx})\n"
    except Exception as e:
        text += f"Error: {str(e)}"
        
    return text

if __name__ == "__main__":
    msg = run_fw_list()
    wrtapi.send_message(wrtapi.CHAT_ID, msg)
