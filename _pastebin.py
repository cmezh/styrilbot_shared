# -*- coding: utf-8 -*-

from _util import dbg
import config
from pastebin import PastebinAPI, PastebinError
from requests import get

class pastebin:
  def __init__(self):
    self.pb = PastebinAPI()

  def getkey(self, title):
    dbg("getkey function entrypoint")
    try:
      pastes = self.pb.pastes_by_user(config.pastebin_devkey, config.pastebin_userkey)
    except PastebinError:
      dbg("PastebinError: no pastes?")
      return None
    key = pastes.split("<paste_title>%s</paste_title>" % title)[0]
    key = key.split("<paste_key>")[1]
    key = key.split("</paste_key>")[0]
    dbg("returning key: %s" % key)
    return key

  def getpaste(self, key):
    dbg("getpaste function entrypoint")
    url = "https://pastebin.com/raw/%s" % key
    content = get(url).content.decode("utf-8")
    return content

  def paste(self, title, content):
    dbg("paste function entrypoint")
    key = self.pb.paste(config.pastebin_devkey, content, config.pastebin_userkey, paste_name=title, paste_format="json")
    key = key.split("/")[-1]
    dbg("return value is %s" % key)
    return key

  def deletepaste(self, key):
    dbg("deletepaste function entrypoint")
    self.pb.delete_paste(config.pastebin_devkey, config.pastebin_userkey, key)
