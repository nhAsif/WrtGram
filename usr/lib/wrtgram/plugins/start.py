#!/usr/bin/env python3
import sys, os

sys.path.append("/usr/lib/wrtgram")
import wrtapi

def run_start():
    text = "I can help you to manage and get some information about your OpenWRT Router.\n"
    text += "This is the available commands list:\n\n"
    
    plugins_dir = "/usr/lib/wrtgram/plugins"
    help_dir = os.path.join(plugins_dir, "help")
    
    # Get all files in plugins dir that are not subdirectories
    try:
        plugins = [f for f in os.listdir(plugins_dir) 
                   if os.path.isfile(os.path.join(plugins_dir, f)) and not f.endswith(".py")]
        # Also include .py plugins but without the extension
        py_plugins = [f[:-3] for f in os.listdir(plugins_dir) 
                      if os.path.isfile(os.path.join(plugins_dir, f)) and f.endswith(".py") 
                      and f != "wrtapi.py" and not f.startswith("__")]
        
        all_plugins = sorted(list(set(plugins + py_plugins)))
        
        for plug in all_plugins:
            # Skip internal or utility scripts if any
            if plug in ["common", "wrtapi"]: continue
            
            help_text = ""
            help_file = os.path.join(help_dir, plug)
            if os.path.exists(help_file):
                with open(help_file, "r") as hf:
                    help_text = hf.read().strip()
            
            if not help_text:
                help_text = "No description available"
                
            text += f"[/{plug}](/{plug}) - {help_text}\n"
    except Exception as e:
        text += f"Error listing commands: {str(e)}"
        
    return text

if __name__ == "__main__":
    msg = run_start()
    wrtapi.send_message(wrtapi.CHAT_ID, msg)
