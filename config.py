# -*- coding: utf-8 -*-
telegram_id = #integer
telegram_token = ''
reddit_id = ""
reddit_secret = ""
reddit_token = ""
pastebin_devkey = ""
pastebin_userkey = ""
bind_addr = "" #iface ip
default_port = 8080
server_route = "/bot"
webhook_url = ""
eraser_keywords = ["someword1", "someword2"]
sendas_rights = [12345678, 23456789] #users' ids
sendas_aliases = {"@alias": -6542234565433,
                  "@alias2": 135798642357} #group chats' aliases and ids

autoreply_rules = [{"match_type": "text", #text|sticker_set
                    "match_content": ["testworwd5"], #keywords
                    "reply_type": "text", #text|picture
                    "reply_content": "testreply5"}, #reply text
                   {"match_type": "sticker_set", #text|sticker_set
                    "match_content": ["Shkya"], #sticker set names
                    "reply_type": "picture", #text|picture
                    "reply_content": "https://i.imgur.com/5cKpzSU.jpg"}] #url

debug = True
duduud
