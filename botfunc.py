#!/usr/bin/env python
# -*- coding: utf-8 -*-

from _util import dbg, sendmedia
import config
from telebot.apihelper import ApiException as TelegramException
from _reddit import RedditException

class BotFunc():

  def __mass_replace(self, source):
    ret = source.replace("а", "a")
    ret = ret.replace("в", "b")
    ret = ret.replace("с", "c")
    ret = ret.replace("е", "e")
    ret = ret.replace("н", "h")
    ret = ret.replace("к", "k")
    ret = ret.replace("м", "m")
    ret = ret.replace("о", "o")
    ret = ret.replace("р", "p")
    ret = ret.replace("т", "t")
    ret = ret.replace("х", "x")
    ret = ret.replace("у", "y")
    return ret

  def __init__(self, bot, reddit):
    self.bot = bot
    self.reddit = reddit
    self.func = [{"function": self.eraser,
                  "filters": {}},
                 {"function": self.com_r,
                  "filters": {"commands": ["r"]}},
                 {"function": self.com_d,
                  "filters": {"commands": ["d"]}},
                 {"function": self.com_me,
                  "filters": {"commands": ["me"]}}]

    self.eraser_match = ['тееееест']

    for i in range(len(self.eraser_match)):
      self.eraser_match[i] = self.__mass_replace(self.eraser_match[i].lower())

  def com_r(self, message):
    dbg("Got r command: %s" % message.text)
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

  def eraser(self, message):
    if message.text:
      exam = self.__mass_replace(message.text.lower())
    elif message.caption:
      exam = self.__mass_replace(message.caption.lower())
    else:
      return

    for match in self.eraser_match:
      if match in exam:
        try:
          self.bot.delete_message(message.chat.id, message.message_id)
        except TelegramException:
          pass
        return
