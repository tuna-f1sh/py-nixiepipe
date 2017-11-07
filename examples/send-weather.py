import sys
import os
import time
import signal
import nixiepipe
import threading
import pyowm
import configparser
import datetime

# Load API key from config file in examples directory
config = configparser.ConfigParser()

# Create file with API key in format shown https://docs.python.org/3/library/configparser.html
config.read(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'owm-api.ini'))

owm = pyowm.OWM(config['API']['OpenWeatherMap'])  # You MUST provide a valid API key in owm-api.ini in same folder as script

global w

class RepeatedTimer(object):
    def __init__(self, interval, function, *args, **kwargs):
        self._timer     = None
        self.interval   = interval
        self.function   = function
        self.args       = args
        self.kwargs     = kwargs
        self.is_running = False
        self.start()

    def _run(self):
        self.is_running = False
        self.start()
        self.function(*self.args, **self.kwargs)

    def start(self):
        if not self.is_running:
            self._timer = threading.Timer(self.interval, self._run)
            self._timer.start()
            self.is_running = True

    def stop(self):
        self._timer.cancel()
        self.is_running = False

# catch ctrl-c to gracefully close
def sigint_handler(signum, frame):
    print('Ctrl-C detected, closing port...')
    pipes.close()
    weatherTask.stop()
    sys.exit()

def updateweather():
    print('Weather update')
    # Search for current weather in London (UK)
    observation = owm.weather_at_place('Bristol,uk')
    global w
    w = observation.get_weather()
    print(w.get_detailed_status())
    pipes.sendWeather(w.get_temperature('celsius')['temp'],w.get_weather_icon_name(),w.get_humidity(), w.get_wind()['speed'])

signal.signal(signal.SIGINT, sigint_handler)

if len(sys.argv) > 1:
    pipes = nixiepipe.pipe(sys.argv[1])
else:
    pipes = nixiepipe.pipe()

# Grab weather on first run and setup timer task to update
updateweather()
weatherTask = RepeatedTimer(60*30, updateweather)

pipes.setPipeColour(0,255,128,0)

now = datetime.datetime.now()

pipes.sendTime(now.hour, now.minute)

while (True):
    input("Sending weather data every 30 minutes, press [ENTER] key to quit")
    pipes.close()
    weatherTask.stop()
    sys.exit()
