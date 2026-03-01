#!/usr/bin/env python3
# HELP: This menu help!
import sys, os

sys.path.append("/usr/lib/wrtgram")
import wrtapi

def run_start():
    text = "I can help you to manage and get some information about your OpenWRT Router.\n"
    text += "This is the available commands list:\n\n"
    
    plugins_dir = "/usr/lib/wrtgram/plugins"
    
    try:
        # Get all files in plugins dir that are not subdirectories or helper modules
        plugins = [f for f in os.listdir(plugins_dir) 
                   if os.path.isfile(os.path.join(plugins_dir, f)) and not f.endswith(".py")]
        py_plugins = [f[:-3] for f in os.listdir(plugins_dir) 
                      if os.path.isfile(os.path.join(plugins_dir, f)) and f.endswith(".py") 
                      and f != "wrtapi.py" and not f.startswith("__")]
        
        all_plugins = sorted(list(set(plugins + py_plugins)))
        
        for plug in all_plugins:
            if plug in ["common", "wrtapi"]: continue
            
            help_text = wrtapi.get_plugin_help(plug)
            if not help_text:
                help_text = "No description available"
                
            text += f"[/{plug}](/{plug}) - {help_text}\n"
    except Exception as e:
        text += f"Error listing commands: {str(e)}"
        
    return text

if __name__ == "__main__":
    msg = run_start()
    wrtapi.send_message(wrtapi.CHAT_ID, msg)
