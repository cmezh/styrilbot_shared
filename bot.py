#!/usr/bin/env python
# -*- coding: utf-8 -*-

import config
from _util import dbg, sendmedia
import telebot
from _reddit import RedditWrapper
from os import environ
from flask import Flask, request
from botfunc import BotFunc

dbg("Creating TeleBot instance")
bot = telebot.TeleBot(config.telegram_token, threaded=False)
dbg("Creating Reddit instance")
reddit = RedditWrapper()
dbg("Creating Flask instance")
server = Flask(__name__)

@server.route(config.server_route, methods=['POST'])
def getMessage():
#  dbg("Got new request to server")
  bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
  return "!", 200

@server.route("/bot", methods=["POST"])
def oldMessage():
  return "!", 200

for func in BotFunc(bot, reddit).func:
  bot.add_message_handler(func)
  bot.add_edited_message_handler(func)

dbg("Running server")
server.run(host=config.bind_addr, port=environ.get('PORT', config.default_port))
dbg("Setting webhook")
bot.remove_webhook()
bot.set_webhook(url=config.webhook_url)
