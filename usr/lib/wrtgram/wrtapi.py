import sys, os, subprocess, json, time, re

def get_uci(path, default=""):
    try:
        return subprocess.check_output(["uci", "-q", "get", path]).decode('utf-8').strip()
    except Exception:
        return default

URL = get_uci("wrtgram.global.url")
KEY = get_uci("wrtgram.global.key")
WRTGRAM_API = f"{URL}{KEY}" if URL and KEY else ""
CHAT_ID = get_uci("wrtgram.global.my_chat_id")
TLS_INSECURE = get_uci("wrtgram.global.tls_insecure") == "1"
t_str = get_uci("wrtgram.global.timeout", "60")
TIMEOUT = int(t_str) if t_str.isdigit() else 60

def log_msg(name, msg):
    try:
        proc = subprocess.Popen(["logger", "-t", f"{name}[{os.getpid()}]", "-p", "daemon.info"], stdin=subprocess.PIPE)
        proc.communicate(msg.encode('utf-8'))
    except:
        pass

def tg_api_call(endpoint, form_data=None, data_urlencode=None, method="POST", attempts=3, timeout=2):
    if not WRTGRAM_API: return None
    
    cmd = ["curl", "-s"]
    if TLS_INSECURE:
        cmd.append("-k")
    else:
        cmd.extend(["--capath", "/etc/ssl/certs"])
        
    cmd.extend(["-X", method, f"{WRTGRAM_API}/{endpoint}"])
    
    if form_data:
        for k, v in form_data.items():
            cmd.extend(["-d", f"{str(k)}={str(v)}"])
            
    if data_urlencode:
        for k, v in data_urlencode.items():
            cmd.extend(["--data-urlencode", f"{str(k)}={str(v)}"])
            
    for attempt in range(attempts):
        try:
            output = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
            if output:
                return json.loads(output.decode('utf-8'))
        except:
            pass
        if attempt < attempts - 1:
            time.sleep(timeout)
    return None

def send_message(chat_id, text, parse_mode="Markdown", reply_markup=None):
    form_data = {"chat_id": chat_id, "parse_mode": parse_mode}
    if reply_markup:
        form_data["reply_markup"] = json.dumps(reply_markup) if isinstance(reply_markup, dict) else reply_markup
    return tg_api_call("sendMessage", form_data=form_data, data_urlencode={"text": text})

def make_keyboard(buttons, row_width=1):
    """
    buttons: list of dicts like {"text": "...", "callback_data": "..."}
    or list of lists for custom structure.
    """
    if buttons and isinstance(buttons[0], list):
        return {"inline_keyboard": buttons}
        
    keyboard = []
    for i in range(0, len(buttons), row_width):
        keyboard.append(buttons[i : i + row_width])
    return {"inline_keyboard": keyboard}

def paginate_buttons(items, page, page_size, callback_pattern):
    """
    items: list of buttons
    callback_pattern: string with {page} placeholder for navigation buttons
    """
    total_pages = (len(items) + page_size - 1) // page_size
    if total_pages <= 1:
        return items
        
    if page < 1: page = 1
    if page > total_pages: page = total_pages
    
    start = (page - 1) * page_size
    end = start + page_size
    
    page_items = items[start:end]
    
    nav_row = []
    if page > 1:
        nav_row.append({"text": "⬅️ Prev", "callback_data": callback_pattern.format(page=page-1)})
    
    nav_row.append({"text": f"{page}/{total_pages}", "callback_data": "ignore|"})
    
    if page < total_pages:
        nav_row.append({"text": "Next ➡️", "callback_data": callback_pattern.format(page=page+1)})
        
    page_items.append(nav_row)
    return page_items
