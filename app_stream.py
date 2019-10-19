"""
app_stream.py - Control lights through local GPIO based on contents of twitter feed.

From: https://developer.twitter.com/en/docs/labs/filtered-stream/quick-start

Copyright (c) 2019 by Thomas J. Daley, J.D. All Rights Reserved.
"""
import os
import requests
import json
import RPi.GPIO as GPIO
from threading import Thread
from threading import Timer
import time
from pprint import pprint
from requests.auth import AuthBase
from requests.auth import HTTPBasicAuth

DEBUG = False
LIGHT_ON_DURATION_SECS = 30.0
AGENT_NAME = "AnalyzeMyTweets"
PINS = [11, 13, 15, 16]  # physical locations on the GPIO strip

STREAM_URL = "https://api.twitter.com/labs/1/tweets/stream/filter"
RULES_URL = "https://api.twitter.com/labs/1/tweets/stream/filter/rules"

# Rules are documented here: https://developer.twitter.com/en/docs/labs/filtered-stream/operators
RULES = [
  { 'value': '#avianaart has:images -sucks -ugly -horrible', 'tag': 'avianaart' },
  { 'value': '#avianaart -sucks -ugly -horrible', 'tag': 'art-no-images'},
  { 'value': '@avianaart7 -sucks -ugly -horrible', 'tag': 'art-ats'}
]

class LightController(Thread):
    """
    Encapsulates the light control.
    """
    def __init__(self, pins):
        self.pins = pins
        self.lights_are_on = False
        self.init_gpio()

    def init_gpio(self):
        """
        Initialize the GPIO interface.
        """
        # Supress warnings
        GPIO.setwarnings(False)

        # Reference channels by physical pin number.
        GPIO.setmode(GPIO.BOARD)

        # Set the pins to output mode.
        for pin in self.pins:
            GPIO.setup(pin, GPIO.OUT)
            if DEBUG:
                print("Setup GPIO pin", pin)

        # Flash the lights to indicate that we are up and running.
        self.flash(count=2)

    def flash(self, count: int=2):
        """
        Flash the A/C circuit *count* times.
        """

        for i in range(count):
            self.lights_on(auto_off=False)
            time.sleep(2)
            self.lights_off()
            time.sleep(2)


    def lights_on(self, auto_off: bool=True):
        """
        Turn the lights on.
        """
        if self.lights_are_on:
            return

        self.lights_are_on = True

        for pin in self.pins:
            GPIO.output(pin, GPIO.LOW)
            if DEBUG:
                print("LIGHTS ON:", pin)

        if auto_off:
            off_timer = Timer(LIGHT_ON_DURATION_SECS, self.lights_off)
            off_timer.start()

    def lights_off(self):
        """
        Turn the lights off.
        """
        for pin in self.pins:
            GPIO.output(pin, GPIO.HIGH)
            if DEBUG:
                print("LIGHTS OFF:", pin)

        self.lights_are_on = False

# Set-up the GPIO controller
light_controller = LightController(PINS)

# Gets a bearer token
class BearerTokenAuth(AuthBase):
  def __init__(self):
    self.bearer_token_url = "https://api.twitter.com/oauth2/token"
    self.consumer_key = CONSUMER_KEY  # os.environ["CONSUMER_KEY"]
    self.consumer_secret = CONSUMER_SECRET  # os.environ["CONSUMER_SECRET"]
    self.bearer_token = self.get_bearer_token()

  def get_bearer_token(self):
    response = requests.post(
      self.bearer_token_url, 
      auth=(self.consumer_key, self.consumer_secret),
      data={'grant_type': 'client_credentials'},
      headers={'User-Agent': AGENT_NAME})

    if response.status_code is not 200:
      raise Exception(f"Cannot get a Bearer token (HTTP %d): %s" % (response.status_code, response.text))

    body = response.json()
    return body['access_token']

  def __call__(self, r):
    r.headers['Authorization'] = f"Bearer %s" % self.bearer_token
    r.headers['User-Agent'] = AGENT_NAME
    return r


def get_all_rules(auth):
  response = requests.get(RULES_URL, auth=auth)

  if response.status_code is not 200:
    raise Exception(f"Cannot get rules (HTTP %d): %s" % (response.status_code, response.text))

  return response.json()


def delete_all_rules(rules, auth):
  if rules is None or 'data' not in rules or len(rules['data']) == 0:
    return None

  ids = list(map(lambda rule: rule['id'], rules['data']))

  payload = {
    'delete': {
      'ids': ids
    }
  }

  response = requests.post(RULES_URL, auth=auth, json=payload)

  if response.status_code is not 200:
    raise Exception(f"Cannot delete rules (HTTP %d): %s" % (response.status_code, response.text))

def set_rules(rules, auth):
  if rules is None:
    return

  payload = {
    'add': rules
  }

  response = requests.post(RULES_URL, auth=auth, json=payload)

  if response.status_code is not 201:
    raise Exception(f"Cannot create rules (HTTP %d): %s" % (response.status_code, response.text))

def stream_connect(auth):
  response = requests.get(STREAM_URL, auth=auth, stream=True)
  for response_line in response.iter_lines():
    if response_line:
      pprint(json.loads(response_line))
      light_controller.lights_on()

bearer_token = BearerTokenAuth()

def setup_rules(auth):
  current_rules = get_all_rules(auth)
  delete_all_rules(current_rules, auth)
  set_rules(RULES, auth)


# Comment this line if you already setup rules and want to keep them
setup_rules(bearer_token)

# Listen to the stream.
# This reconnection logic will attempt to reconnect when a disconnection is detected.
# To avoid rate limites, this logic implements exponential backoff, so the wait time
# will increase if the client cannot reconnect to the stream.
timeout = 0
while True:
  stream_connect(bearer_token)
  time.sleep(2 ** timeout)
  timeout += 1
