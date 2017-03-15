import sys
import time
import signal
import nixiepipe
import random

# catch ctrl-c to gracefully close
def sigint_handler(signum, frame):
    print('Ctrl-C detected, closing port...')
    pipe.close()
    sys.exit()

signal.signal(signal.SIGINT, sigint_handler)

if len(sys.argv) > 1:
    pipe = nixiepipe.pipe(sys.argv[1])
else:
    pipe = nixiepipe.pipe()

pipe.setNumberUnits(0)
pipe.setColour(255,255,255)
pipe.setPipeColour(0,255,128,0)

while(True):
    pipe.setNumber(random.randint(0,9999))
    pipe.setColour(random.randint(0,255),random.randint(0,255),random.randint(0,255))
    pipe.show()
    time.sleep(0.5)
