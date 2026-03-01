import subprocess, json, sys, os
sys.path.append("/usr/lib/wrtgram")
import wrtapi

def get_uci_list(config, section_type, filter_attr=None):
    """
    Returns a list of dicts with 'id' and 'name' (or other descriptive attribute).
    """
    try:
        out = subprocess.check_output(["uci", "-q", "show", f"{config}"], stderr=subprocess.DEVNULL).decode('utf-8')
        sections = []
        seen_ids = set()
        
        for line in out.splitlines():
            if f".@{(section_type)}[" in line and "=" in line:
                part = line.split('=')[0]
                idx = part.split('[')[-1].split(']')[0]
                sec_id = f"{section_type}[{idx}]"
                if sec_id not in seen_ids:
                    seen_ids.add(sec_id)
                    name = wrtapi.get_uci(f"{config}.@{sec_id}.name")
                    if not name:
                        name = wrtapi.get_uci(f"{config}.@{sec_id}.label")
                    if not name:
                        if config == "network":
                            name = wrtapi.get_uci(f"{config}.@{sec_id}.ifname")
                        elif config == "wireless":
                            name = wrtapi.get_uci(f"{config}.@{sec_id}.ssid")
                            
                    if not name:
                        name = f"Unnamed {section_type} {idx}"
                        
                    enabled = wrtapi.get_uci(f"{config}.@{sec_id}.enabled", "1")
                    name_display = name
                    if enabled == "0":
                        name_display += " (Disabled)"
                    elif enabled == "1" and config == "firewall":
                         name_display += " (Enabled)"
                         
                    sections.append({
                        "id": idx,
                        "name": name,
                        "display": name_display
                    })
        return sections
    except:
        return []

def get_items(ctx_type):
    if ctx_type == "firewall_rule":
        return get_uci_list("firewall", "rule")
    elif ctx_type == "firewall_redirect":
        return get_uci_list("firewall", "redirect")
    elif ctx_type == "interface":
        try:
            out = subprocess.check_output(["ubus", "list", "network.interface.*"], stderr=subprocess.DEVNULL).decode('utf-8')
            items = []
            for line in out.splitlines():
                name = line.split('.')[-1]
                items.append({"id": name, "name": name, "display": name})
            return items
        except:
            return []
    elif ctx_type == "wifi":
        try:
            out = subprocess.check_output(["uci", "-q", "show", "wireless"], stderr=subprocess.DEVNULL).decode('utf-8')
            items = []
            for line in out.splitlines():
                if "default_radio" in line and ".ssid=" in line:
                    idx = line.split('.')[0].replace("wireless", "")
                    ssid = line.split('=')[-1].strip("'")
                    items.append({"id": idx, "name": ssid, "display": ssid})
            return items
        except:
            return []
    elif ctx_type == "service":
        try:
            services = os.listdir("/etc/init.d/")
            items = []
            for s in sorted(services):
                items.append({"id": s, "name": s, "display": s})
            return items
        except:
            return []
    return []

def send_ctx_list(chat_id, ctx_type, command, prompt, page=1, page_size=10, is_update=False, message_id=None):
    items_data = get_items(ctx_type)
    buttons = []
    for item in items_data:
        buttons.append({
            "text": item["display"],
            "callback_data": f"{command}|{item['id']}^{item['name']}"
        })
        
    pattern = f"ctx_relist|{ctx_type},{command},{{page}},{prompt}"
    
    paginated_buttons = wrtapi.paginate_buttons(buttons, page, page_size, pattern)
    keyboard = wrtapi.make_keyboard(paginated_buttons)
    
    if is_update and message_id:
        return wrtapi.tg_api_call("editMessageText", 
                                  form_data={"chat_id": chat_id, "message_id": message_id, "parse_mode": "Markdown", "reply_markup": json.dumps(keyboard)},
                                  data_urlencode={"text": prompt})
    else:
        return wrtapi.tg_api_call("sendMessage", 
                                  form_data={"chat_id": chat_id, "parse_mode": "Markdown", "reply_markup": json.dumps(keyboard)},
                                  data_urlencode={"text": prompt})
