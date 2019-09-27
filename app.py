import RPi.GPIO as GPIO
import time

def main(args):
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
