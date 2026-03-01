#!/usr/bin/env python3
import sys, os

# Add paths for wrtapi and ctx helper
sys.path.append("/usr/lib/wrtgram")
sys.path.append("/usr/lib/wrtgram/plugins/ctx")

import wrtapi
import helper

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("0|Missing parameters")
        sys.exit(0)
        
    # Parameter format: ctx_type,command,page,prompt
    params = sys.argv[1].split(',', 3)
    if len(params) < 4:
        print("0|Invalid parameters")
        sys.exit(0)
        
    ctx_type, command, page_str, prompt = params
    try:
        page = int(page_str)
    except:
        page = 1
        
    # We are updating an existing message
    # The telegram_bot passes WRTGRAM_CHAT_ID and handles the response if we follow its format.
    # However, the bot's action handler expect the output in format: remove|msg|keyboard
    # And it calls editMessageText using that.
    
    items_data = helper.get_items(ctx_type)
    buttons = []
    for item in items_data:
        buttons.append({
            "text": item["display"],
            "callback_data": f"{command}|{item['id']}^{item['name']}"
        })
        
    pattern = f"ctx_relist|{ctx_type},{command},{{page}},{prompt}"
    paginated_buttons = wrtapi.paginate_buttons(buttons, page, 10, pattern)
    keyboard = wrtapi.make_keyboard(paginated_buttons)
    
    # Format for telegram_bot action handler: 1 (update) | message_text | keyboard_json
    import json
    print(f"1 | {prompt} | {json.dumps(keyboard)}")
