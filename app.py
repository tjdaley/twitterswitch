import RPi.GPIO as GPIO
import json
import time
import twitter

# TODO: Turn these into command line arguments OR config file parameters
HASHTAG = "%23avianaart"
QUERY = f'q={HASHTAG}&result_type=recent&since_id='
PINS = [11, 13, 15, 16]  # physical locations on the GPIO strip

def setup_gpio(pins: list):
  """
  Set up the GPIO. This will elect to address pins by physical location number.
  
  Args:
    pins (list): List of pin numbers connected to the relay board.
  """
  # Supress warnings
  GPIO.setwarnings(False)
  
  # Reference channels by physical pin number.
  GPIO.setmode(GPIO.BOARD)
  
  # Set the pins to output mode.
  for pin in pins:
    GPIO.setup(pin, GPIO.OUT)

def lights_on(pins: list):
  """
  Turn the lights on.
  """
  for pin in pins:
    GPIO.output(pin, GPIO.LOW)


def lights_off(pins: list):
  """
  Turn the lights off.
  """
  for pin in pins:
    GPIO.output(pin, GPIO.HIGH)


def cleanup():
  """
  Clean up before exiting.
  """
  GPIO.cleanup()


def load_keys():
  with open ("../keys.json", "r") as key_file:
    keys = json.load(key_file)
  return keys


def connect_twitter(config):
  """
  Connect to Twitter.
  
  Args:
    config (tuple): Contains the parameters needed to authenticate and authorize with Twitter.

  Returns:
    Reference to connected Twitter service.
  """
  api = twitter.Api(consumer_key=config["CONSUMER_KEY"],
                    consumer_secret=config["CONSUMER_SECRET"],
                    access_token_key=config["ACCESS_TOKEN_KEY"],
                    access_token_secret=config["ACCESS_TOKEN_SECRET"],
                    sleep_on_rate_limit=True)

  verified_credentials = api.VerifyCredentials()
  # print("Screen name:", verified_credentials.screen_name)
  # print("Last Tweet:", verified_credentials.status.text)
  return api


def search_twitter(api, last_id: str):
  results = []
  try:
    results = api.GetSearch(raw_query=QUERY+last_id)
  except twitter.error.TwitterError as e:
    print(str(e))
    print(QUERY)

  return results


def log_tweet(tweet: dict):
  message = f"{tweet.created_at} - {tweet.user.name} at {tweet.user.location}"
  print(message)


def main(args):
    api = connect_twitter(load_keys())
    setup_gpio(PINS)
    
    last_id = "0"

    while True:
      results = search_twitter(api, last_id)
      if len(results) > 0:
        # print(results[0].text)
        last_id = results[0].id_str
        log_tweet(results[0])
        lights_on(PINS)
        time.sleep(60)
        lights_off(PINS)
      time.sleep(4)

if __name__ == "__main__":
  try:
    main(None)
  except Exception as e:
    print(str(e))
    
  cleanup()
  exit()
