import RPi.GPIO as GPIO
import json
import time
import twitter

QUERY = 'q=%23avianaart%20near%3A"3011%20chukar%20dr%2C%20mckinney%2C%20tx"%20within%3A15mi&src=typd'
PINS = [11, 13, 15, 16]

def setup_gpio(pins: list):
  """
  Set up the GPIO. This will elect to address pins by physical location number.
  
  Args:
    pins (list): List of pin numbers connected to the relay board.
  """
  
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
  api = twitter.Api(consumer_key=config["consumer_key"],
                    consumer_secret=config["consumer_secret"],
                    access_token_key=config["access_token_key"],
                    access_token_secret=config["access_token_secret"],
                    sleep_on_rate_limit=True)

  verified_credentials = api.VerifyCredentials()
  return api


def search_twitter(last_date: str):
  results = api.GetSearch(raw_query=QUERY)
  return results


def main(args):
    api = connect_twitter(load_keys())
    setup_gpio(PINS)
    
    last_date = ""

    while True:
      results = search_twitter(last_date)
      print(results)
      time.sleep(30)

def xmain(args):
  print("Starting . . .")
  pins = [11, 13, 15, 16]
  
  # Reference channels by physical pin number
  print("Reference pins by physical board position.")
  GPIO.setmode(GPIO.BOARD)
  
  for pin in pins:
    print(f"Setting pin {pin} to output mode")
    GPIO.setup(pin, GPIO.OUT)

  for pin in pins:
    print(f"Raising pin {pin}")
    GPIO.output(pin, GPIO.LOW)
    
  print("Sleeping for 10 seconds")
  time.sleep(10)
  
  for pin in pins:
    print(f"Droping pin {pin}")
    GPIO.output(pin, GPIO.HIGH)
  
  print("Sleeping another 10 seconds")
  time.sleep(10)
  print("Cleaning up")
  GPIO.cleanup()
    
  
if __name__ == "__main__":
  main(None)
