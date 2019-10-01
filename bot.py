#!/usr/bin/env python

import config
from _util import dbg, sendmedia
import telebot
from _reddit import RedditWrapper, RedditException
from os import environ
from flask import Flask, request

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

dbg("Running server")
server.run(host="0.0.0.0", port=environ.get('PORT', 80))
dbg("Setting webhook")
bot.remove_webhook()
bot.set_webhook(url="https://styrilbot.herokuapp.com/bot")
