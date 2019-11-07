#!/usr/bin/env python
# -*- coding: utf-8 -*-

import config
from _util import dbg, sendmedia
import telebot
from _reddit import RedditWrapper, RedditException
from os import environ
from flask import Flask, request
from random import random

dbg("Creating TeleBot instance")
bot = telebot.TeleBot(config.telegram_token, threaded=False)
dbg("Creating Reddit instance with  mkreddit() function")
reddit = RedditWrapper()
dbg("Creating Flask instance")
server = Flask(__name__)

@server.route("/bot", methods=['POST'])
def getMessage():
#  dbg("Got new request to server")
  bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
  return "!", 200

#@bot.message_handler(commands=["start"])
#def com_start(message):
#  dbg("Got start command")
#  bot.send_message(message.chat.id, "Ты чё пёс я щас те флешку зашью")

@bot.message_handler(commands=["r"])
def com_r(message):
  dbg("Got r command: %s" % message.text)
  if random() < 0.01:
    dbg("Got random match")
    bot.send_message(message.chat.id, "Ты чё пёс я щас те флешку зашью", reply_to_message_id=message.message_id)
    return
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
      try:
        bot.delete_message(message.chat.id, message.message_id)
      except telebot.apihelper.ApiException:
        pass
    else:
      bot.send_message(message.chat.id, "Sorry. No.", reply_to_message_id=message.message_id)
  else:
    bot.send_message(message.chat.id, "Command should be sent in reply to message that you want to be deleted", reply_to_message_id=message.message_id)

@bot.message_handler(commands=["me"])
def com_me(message):
  dbg("Got me command")
  if len(message.text.split(" ")) > 1:
    try:
      bot.delete_message(message.chat.id, message.message_id)
      sender = message.from_user.first_name
      if message.from_user.last_name: sender += " %s" % message.from_user.last_name
      msg = "* %s %s" % (sender, " ".join(message.text.split(" ")[1:]))
      bot.send_message(message.chat.id, msg)
    except telebot.apihelper.ApiException:
      pass

dbg("Running server")
server.run(host="0.0.0.0", port=environ.get('PORT', 80))
dbg("Setting webhook")
bot.remove_webhook()
bot.set_webhook(url="https://styrilbot.herokuapp.com/bot")
