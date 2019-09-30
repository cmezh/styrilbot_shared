#!/usr/bin/env python

import config
import os, sys
from requests import get, head
from json import loads
#from magic import from_file as magic

def dbg(msg):
  if config.debug: print("--- %s" % msg)

def sendmedia(bot, media, message):
  dbg("send_img function entrypoint")
  cid = message.chat.id
  msgid = message.message_id
  url = media[0]
  ext = media[1]

  dbg("Downloading media, url is %s" % url)
  with open("tmp." + ext, "wb") as h:
    resp = get(url).content
    h.write(resp)
  if ext == "gif":
    dbg("Sending gif as document")
    bot.send_document(cid, open("tmp." + ext, "rb"), reply_to_message_id=msgid)
  elif ext == "mp4":
    dbg("Sending mp4 as video")
    bot.send_video(cid, open("tmp." + ext, "rb"), reply_to_message_id=msgid)
  else:
    dbg("Sending whatever it is as photo")
    bot.send_photo(cid, open("tmp." + ext, "rb"), reply_to_message_id=msgid)
  dbg("Removing temp file")
  os.remove("tmp." + ext)

def mediamatch(url):
  dbg("mediamatch function entrypoint")
  url = url.split("?")[0]
  dbg("url is %s" % url)
  if url.endswith((".jpg", ".png", ".gif", ".mp4", ".gifv")):
    if url.endswith(".gifv"): url = url.replace(".gifv", ".mp4")
    if head(url).status_code != 200: return None
    return url, url.split(".")[-1]
  else:
    return None

def gfycat(url):
  part = url.split("/")[-1]
  json_url = "https://api.gfycat.com/v1/gfycats/%s" % part
  json_dict = loads(get(json_url).content)
  url = json_dict["gfyItem"]["gifUrl"]
  return url, url.split(".")[-1]

def vreddit(url):
  final_url = get(url).url
  dbg("Final url: %s" % final_url)
  json_url = "%s.json" % final_url
  json_dict = loads(get(json_url).content)
  try:
    url = json_dict[0]['data']['children'][0]['data']['secure_media']['reddit_video']['fallback_url']
  except:
    return None
  return url, "mp4"

