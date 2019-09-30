import config
from _util import dbg, mediamatch, gfycat, vreddit
from _pastebin import pastebin
from praw import Reddit
from prawcore import OAuthException, NotFound, BadRequest, Forbidden, Redirect
from random import choice
from re import match
from requests import get
from urllib.error import HTTPError
from json import loads, dumps
from datetime import datetime
from os.path import exists
from Crypto.Cipher import AES
import base64

class RedditException(Exception):
  pass

class RedditWrapper:
  def __init__(self):
    self.client_id = config.reddit_id
    self.client_secret = config.reddit_secret
    self.refresh_token = config.reddit_token
    self.gfycat_re = "^https://gfycat\.com/[A-Za-z]+$"
    self.vreddit_re = "^https://v.redd.it/[0-9A-za-z]+$"
    self.pb = pastebin()
    self.cachefile = "re.c"
    self.cachekey = None
    self.reddit = self.mkreddit()
    self.cache = {}
    self.cipher = AES.new(config.reddit_secret[:16], AES.MODE_ECB)
    self.loadcache()

  def clearcache(self):
    dbg("Clearing cache")
    now = datetime.now()
    for sub in self.cache:
      for key in self.cache[sub]:
        delta = (now - self.cache[sub][key]["time"]).days
        if delta >= 3: del self.cache[sub][key]

  def updatecache(self):
    dbg("Updating reddit cache file")
    json_raw = {}
    for sub in self.cache:
      json_raw[sub] = {}
      for key in self.cache[sub]:
        json_raw[sub][key] = { "list": self.cache[sub][key]["list"],
                               "time": self.cache[sub][key]["time"].timestamp() }
    json_str = dumps(json_raw)
    json_str = json_str + " " * (16 - (len(json_str) % 16))
    json_enc = base64.b64encode(self.cipher.encrypt(json_str.encode("utf-8"))).decode("utf-8")
    dbg("Encrypted, len is %d" % len(json_enc))
    if self.cachekey:
      try:
        self.pb.deletepaste(self.cachekey)
      except HTTPError:
        self.cachekey = self.pb.getkey(self.cachefile)
        self.pb.deletepaste(self.cachekey)
    self.cachekey = self.pb.paste(self.cachefile, json_enc)

  def loadcache(self):
    dbg("Loading reddit cache file")
    self.cachekey = self.pb.getkey(self.cachefile)
    if not self.cachekey:
      dbg("No cache paste found")
      return
    json_enc = self.pb.getpaste(self.cachekey)
    json_raw = loads(self.cipher.decrypt(base64.b64decode(json_enc.encode("utf-8"))).decode("utf-8"))
    for sub in json_raw:
      self.cache[sub] = {}
      for key in json_raw[sub]:
        self.cache[sub][key] = { "list": json_raw[sub][key]["list"],
                                 "time": datetime.fromtimestamp(json_raw[sub][key]["time"]) }

  def mkreddit(self):
    dbg("Creating Reddit instance")
    return Reddit(client_id=self.client_id,
                  client_secret=self.client_secret,
                  refresh_token=self.refresh_token,
                  user_agent="styrilbot alpha")

  def requestlist(self, sub, keywords):
    try:
      if keywords:
        dbg("Forming search-by-keywords list in sub %s with keywords %s" % (sub, keywords))
        ret = [u.url for u in list(self.reddit.subreddit(sub).search(keywords, sort="top", limit=500, params={'include_over_18': 'on'}))]
        if not len(ret):
          dbg("Search-by-keywords list is null-length")
          raise RedditException("Nothing found in subreddit '%s' with keywords '%s'" % (sub, " ".join(keywords.split("+"))))
      else:
        dbg("Forming list without keywords in sub %s" % sub)
        ret = [u.url for u in list(self.reddit.subreddit(sub).top(limit=500))]
        if not len(ret):
          raise RedditException("Looks like subreddit '%s' is empty" % sub)
    except NotFound:
      dbg("Got NotFound exception")
      raise RedditException("Subreddit '%s' not found" % sub)
    except Forbidden:
      dbg("Got Forbidden exception")
      raise RedditException("Subreddit '%s' is private" % sub)
    except Redirect:
      dbg("Got Redirect exception")
      raise RedditException("Looks like subreddit '%s' is empty" % sub)
    except BadRequest:
      dbg("Got BadRequest exception")
      raise RedditException("Something went wrong, try again")
    return ret

  def getlist(self, sub, keywords):
    dbg("getlist function entrypoint")
    if sub in self.cache and keywords in self.cache[sub]:
      delta = (datetime.now() - self.cache[sub][keywords]["time"]).days
      if delta >= 3:
        dbg("Cache is old, updating")
        ret = self.requestlist(sub, keywords)
        self.cache[sub][keywords]["list"] = ret
        self.cache[sub][keywords]["time"] = datetime.now()
        self.clearcache()
        self.updatecache()
      else:
        dbg("Using cached list")
        ret = self.cache[sub][keywords]["list"]
    else:
      ret = self.requestlist(sub, keywords)
      if not sub in self.cache: self.cache[sub] = {}
      if not keywords in self.cache[sub]: self.cache[sub][keywords] = {}
      self.cache[sub][keywords]["list"] = ret
      self.cache[sub][keywords]["time"] = datetime.now()
      self.updatecache()
    return ret

  def getmedia(self, sub, subs):
    media = None
    retries = 0
    while not media:
      retries += 1
      if retries > 30:
        dbg("Retries count exceeded")
        raise RedditException("No media of required types found in subreddit '%s' in 30 retries" % sub)
      dbg("Trying to find media in results list, retry #%d of 30" % retries)
      url = choice(subs)
      media = mediamatch(url)
      if not media:
        if match(self.gfycat_re, url):
          dbg("Found gfycat url, retrieving gif url")
          media = gfycat(url)
        elif match(self.vreddit_re, url):
          dbg("Found v.redd.it link, retrieving mp4 url")
          media = vreddit(url)
    return media

  def process(self, command):
    dbg("Processing command")
    args = command.split(" ")
    if len(args) == 1:
      dbg("No subreddit name given")
      raise RedditException("No subreddit name given")

    sub = args[1]
    dbg("Sub is %s" % sub)
    if len(args) > 2:
      keywords = "+".join(args[2:])
      dbg("Keywords are %s" % keywords)
    else:
      keywords = ''
      dbg("No keywords given")

    try:
      dbg("Trying to get list with results")
      subs = self.getlist(sub, keywords)
    except OAuthException:
      dbg("Got OAuthException, creating new Reddit instance")
      self.reddit = self.mkreddit()
      dbg("Rerying to get list with results")
      subs = self.getlist(sub, keywords, message)
    return self.getmedia(sub, subs)


