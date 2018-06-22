#!/usr/bin/env python
from __future__ import print_function, absolute_import, division
from argparse import ArgumentParser as ap
import requests, hashlib, logging, time, json
import subprocess as sp


def get_logger(name = None, loglevel = None, **options):
  logger = logging.getLogger(name or 'cwwwm')
  logger.setLevel(loglevel or logging.INFO)
  logfmt = logging.Formatter(
    fmt='%(levelname)s:%(asctime)s:%(name)s:%(message)s')
  loghnd = logging.StreamHandler()
  loghnd.setFormatter(logfmt)
  logger.addHandler(loghnd)
  return logger


class cwwwmHandler(object):
  def __init__(self, url, slack_url=None, hook_command=None,
               username=None,
               logger=None, title=None, **options):
    self.url = url
    self.slack = slack_url
    self.hook = hook_command
    self.prev_hash = None #self.hash_md5(self.fetch_website())
    self.title = title or url

    self.logger = logger.getChild('web') \
        if logger is not None else get_logger(self.__name__)
    self.logger.debug('cwwwmHandler created for {}'.format(url))

  def __call__(self):
    try:
      curr_text= self.fetch_website()
      curr_hash = self.hash_md5(curr_text)

    except requests.exceptions.RequestException as e:
      self.logger.error(str(e))
      raise Exception(str(e))
    if curr_hash != self.prev_hash:
      self.prev_hash = curr_hash
      self.logger.debug('hash: {}'.format(str(curr_hash)))
      self.logger.info('website {} updated'.format(self.title))

      text = '<{}|{}> updated'.format(self.url,self.title)
      if self.hook is not None:
        hook = sp.Popen([self.hook,], stdin=sp.PIPE, stdout=sp.PIPE)
        hook.stdin.write(curr_text)
        attachment = json.loads(hook.communicate()[0])
        self.logger.info('attach: {}'.format(attachment.keys()))
      else:
        attachment = None

      if self.slack is not None:
        self.post_to_slack(text=text, attachment=attachment)

  def hash_md5(self, text):
    h = hashlib.md5()
    h.update(text)
    return h.hexdigest()

  def fetch_website(self):
    r = requests.get(self.url)
    r.raise_for_status()
    return r.content

  def post_to_slack(self, text, attachment=None):
    return requests.post(
      self.slack, json={'text': text, 'attachments': [attachment,]})


class IntervalTaskExecutor(object):
  def __init__(self, interval, handler, **options):
    self.interval = float(interval)
    self.logger = get_logger(**options)

    self.handler = handler(logger=self.logger, **options)

  def start(self):
    try:
      while True:
        try:
          self.handler()
        except Exception as e:
          self.logger.error(str(e))
        time.sleep(self.interval)
    except KeyboardInterrupt as e:
      self.logger.info('Executor Interrupted: {}'.format(str(e)))


if __name__ == '__main__':
  parser = ap(description='classical website monitoring tool')
  parser.add_argument('url', help='url of the website to be monitored')

  parser.add_argument('--title', type=str, action='store',
                      help='title of the website')
  parser.add_argument('--interval', type=float, action='store', default=3600.,
                      help='monitoring interval in seconds')
  parser.add_argument('--hook', action='store', default=None,
                      help='hook command to post slack')
  parser.add_argument('--slack', action='store', default=None,
                      help='webhook URL of your slack app')
  parser.add_argument('--debug', action='store_const', const='DEBUG',
                      help='enabling debug outputs')

  args = parser.parse_args()

  options = {
    'url': args.url,
    'slack_url': args.slack,
    'hook_command': args.hook,
    'title': args.title,
    'loglevel': args.debug,
  }

  server = IntervalTaskExecutor(args.interval, cwwwmHandler, **options)
  server.start()
