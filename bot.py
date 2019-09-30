#!/usr/bin/env python

import config
from _util import dbg, sendmedia
import telebot
from _reddit import RedditWrapper, RedditException
from _pastebin import pastebin
import os, sys
from flask import Flask, request
from requests import get, head
from random import randint

dbg("Creating TeleBot instance")
bot = telebot.TeleBot(config.telegram_token, threaded=False)
dbg("Creating Reddit instance with  mkreddit() function")
reddit = RedditWrapper()
dbg("Creating Flask instance")
server = Flask(__name__)

pb = pastebin()

@server.route("/bot", methods=['POST'])
def getMessage():
#  dbg("Got new request to server")
  bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
  return "!", 200

#@bot.message_handler(commands=["butts"])
def com_butts(message):
  dbg("Got butts command")
  obutts(message)

#@bot.message_handler(commands=["boobs"])
def com_boobs(message):
  dbg("Got boobs command")
  oboobs(message)

@bot.message_handler(commands=["r"])
def com_r(message):
  dbg("Got r command: %s" % message.text)
  try:
    media = reddit.process(message.text)
    sendmedia(bot, media, message)
  except RedditException as e:
    bot.send_message(message.chat.id, str(e), reply_to_message_id=message.message_id)
    return

@bot.message_handler(commands=["d"])
def com_d(message):
  dbg("Got d command")
  if message.reply_to_message:
    rpl = message.reply_to_message
    if rpl.from_user.id == config.telegram_id:
      bot.delete_message(rpl.chat.id, rpl.message_id)
    else:
      bot.send_message(message.chat.id, "Sorry. No.", reply_to_message_id=message.message_id)
  else:
    bot.send_message(message.chat.id, "Command should be sent in reply to message that you want to be deleted", reply_to_message_id=message.message_id)

@bot.message_handler(commands=["pb"])
def com_pb(message):
  pb.test()

#@bot.message_handler(func=lambda message: True, content_types=["text"])
def msg_process(message):
#  dbg("Message processing")
  if "_станок" in message.text:
    dbg("Found match in message, text is %s" % message.text)
    obutts(message)

def obutts(message):
  dbg("Generating and checking obutts url")
  resp = 0
  while resp != 200:
    url = "http://media.obutts.ru/butts/%05d" % randint(7, 6928)
    ext = ".jpg"
    resp = head(url + ext).status_code
    if resp != 200:
      ext = ".png"
      resp = head(url + ext).status_code
    sendmedia(bot, url + ext, message)

def oboobs(message):
  dbg("Generating and checking oboobs url")
  resp = 0
  while resp != 200:
    url = "http://media.oboobs.ru/boobs/%05d" % randint(1, 14189)
    ext = ".jpg"
    resp = head(url + ext).status_code
    if resp != 200:
      ext = ".png"
      resp = head(url + ext).status_code
    sendmedia(bot, url + ext, message)

dbg("Running server")
server.run(host="0.0.0.0", port=os.environ.get('PORT', 80))
dbg("Setting webhook")
bot.remove_webhook()
bot.set_webhook(url="https://styrilbot.herokuapp.com/bot")
