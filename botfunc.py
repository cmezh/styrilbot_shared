#!/usr/bin/env python
# -*- coding: utf-8 -*-

from _util import dbg, sendmedia
import config
from telebot.apihelper import ApiException as TelegramException
from _reddit import RedditException
from random import random

class BotFunc():
  def __init__(self, bot, reddit):
    self.bot = bot
    self.reddit = reddit
    self.func = [{"function": self.com_r, "filters": {"commands": ["r"]}},
                 {"function": self.com_d, "filters": {"commands": ["d"]}},
                 {"function": self.com_me, "filters": {"commands": ["me"]}}]

  def com_r(self, message):
    dbg("Got r command: %s" % message.text)
    if random() < 0.01:
      dbg("Got random match")
      self.bot.send_message(message.chat.id, "Ты чё пёс я щас те флешку зашью", reply_to_message_id=message.message_id)
      return
    try:
      media = self.reddit.process(message.text)
      sendmedia(self.bot, media, message)
    except RedditException as e:
      self.bot.send_message(message.chat.id, str(e), reply_to_message_id=message.message_id)
      return

  def com_d(self, message):
    dbg("Got d command")
    if message.reply_to_message:
      rpl = message.reply_to_message
      if rpl.from_user.id == config.telegram_id:
        try:
          self.bot.delete_message(rpl.chat.id, rpl.message_id)
          self.bot.delete_message(message.chat.id, message.message_id)
        except TelegramException:
          pass
      else:
        self.bot.send_message(message.chat.id, "Sorry. No.", reply_to_message_id=message.message_id)
    else:
      self.bot.send_message(message.chat.id, "Command should be sent in reply to message that you want to be deleted", reply_to_message_id=message.message_id)

  def com_me(self, message):
    dbg("Got me command")
    if len(message.text.split(" ")) > 1:
      try:
        self.bot.delete_message(message.chat.id, message.message_id)
        sender = "%s %s" % (message.from_user.first_name, message.from_user.last_name) if message.from_user.last_name else message.from_user.first_name
        msg = "* %s %s" % (sender, " ".join(message.text.split(" ")[1:]))
        self.bot.send_message(message.chat.id, msg)
      except TelegramException:
        pass
