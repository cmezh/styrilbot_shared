# -*- coding: utf-8 -*-

import config
import os, sys
from requests import get, head
from json import loads
from telebot.apihelper import ApiException as TelegramException

def dbg(msg):
  if config.debug: print("--- %s" % msg)

def sendmedia(bot, media, message):
  dbg("send_img function entrypoint")
  if message.reply_to_message:
    repl = message.reply_to_message
  else:
    repl = message
  url = media[0]
  ext = media[1]

  dbg("Downloading media, url is %s" % url)
  with open("tmp." + ext, "wb") as h:
    resp = get(url).content
    h.write(resp)
  if ext == "gif":
    dbg("Sending gif as document")
    reply(bot, repl, "doc", open("tmp." + ext, "rb"))
  elif ext == "mp4":
    dbg("Sending mp4 as video")
    reply(bot, repl, "vid", open("tmp." + ext, "rb"))
  else:
    dbg("Sending whatever it is as photo")
    reply(bot, repl, "pic", open("tmp." + ext, "rb"))
  dbg("Removing temp file")
  os.remove("tmp." + ext)

def send_saved_pic(bot, url, message):
  fname = url.split("/")[-1]

  if not os.path.exists(fname):
    with open(fname, "wb") as h:
      resp = get(url).content
      h.write(resp)
  reply(bot, message, "pic", open(fname, "rb"))

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

def reply(bot, message, content_type, content):
  if content_type == "txt":
    func = bot.send_message
  elif content_type == "vid":
    func = bot.send_video
  elif content_type == "pic":
    func = bot.send_photo
  elif content_type == "doc":
    func == bot.send_document

  try:
    dbg("reply 1st stage")
    func(message.chat.id, content, reply_to_message_id=message.message_id)
  except TelegramException:
    try:
      dbg("reply 2nd stage")
      func(message.chat.id, content)
    except TelegramException:
      pass
