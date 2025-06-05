# test_led_sim.py

from src.led_controller import LEDController
from src.speaker import Speaker

leds = LEDController()
speaker = Speaker(led_controller=leds)

speaker.speak("My function is to probe for biological infestations.")
