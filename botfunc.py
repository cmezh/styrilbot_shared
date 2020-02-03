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
    self.func = [{"function": self.sendas,
                  "filters": {"func": self.sendas_match}},
                 {"function": self.eraser,
                  "filters": {"func": self.eraser_match}},
                 {"function": self.com_r,
                  "filters": {"commands": ["r"]}},
                 {"function": self.com_d,
                  "filters": {"commands": ["d"]}},
                 {"function": self.com_me,
                  "filters": {"commands": ["me"]}}]

    self.eraser_keywords = [self.__mass_replace(keyword.lower()) for keyword in config.eraser_keywords]

  def com_r(self, message):
    dbg("Got r command: %s" % message.text)
    try:
      media = self.reddit.process(message.text)
      sendmedia(self.bot, media, message)
    except RedditException as e:
      self.bot.send_message(message.chat.id, str(e), reply_to_message_id=message.message_id)
      return
    except TelegramException:
      pass

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

  def eraser_match(self, message):
    if message.text:
      exam = self.__mass_replace(message.text.lower())
    elif message.caption:
      exam = self.__mass_replace(message.caption.lower())
    else:
      return False

    for keyword in self.eraser_keywords:
      if keyword in exam: return True
    return False

  def eraser(self, message):
    try:
      self.bot.delete_message(message.chat.id, message.message_id)
    except TelegramException:
      pass

  def sendas_match(self, message):
#    dbg(str(message.chat))
#    dbg(str(message.from_user))
    if message.chat.id == message.from_user.id and message.text and message.text.startswith("@"):
      if message.chat.id in config.sendas_rights:
        return True
      else:
        self.bot.send_message(message.chat.id, "Ты недостаточно прав, вот когда будешь достаточно прав -- тогда и будет тебе щастье © 2006, Рыся", reply_to_message_id=message.message_id)
        return False
    else:
      return False

  def sendas(self, message):
    spl = message.text.split()
    if len(spl) < 2: return
    if not spl[0] in config.sendas_aliases:
      self.bot.send_message(message.chat.id, "Неизвестный идентификатор %s" % spl[0], reply_to_message_id=message.message_id)
    else:
      try:
        self.bot.send_message(config.sendas_aliases[spl[0]], " ".join(spl[1:]))
      except TelegramException:
        pass
