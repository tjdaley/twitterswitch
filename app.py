import RPi.GPIO as GPIO
import time

def main(args):
  pins = [11, 13, 15, 16]
  
  # Reference channels by physical pin number
  GPIO.setmode(GPIO.BOARD)
  
  for pin in pins:
    GPIO.setup(pin, GPIO.OUT)

  for pin in pins:
    GPIO.output(pin, GPIO.HIGH)
    
  time.sleep(10)
  
  for in in pins:
    GPIO.output(pin, GPIO.LOW)
    
  GPIO.cleanup()
    
  
  if __name__ == "__main__":
    main(None)
  
