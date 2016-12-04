import sys
import time
import signal

import nixiepipe
from yahoo_finance import Share

# catch ctrl-c to gracefully close
def sigint_handler(signum, frame):
    print 'Ctrl-C detected, closing port...'
    pipe.close()
    sys.exit()

signal.signal(signal.SIGINT, sigint_handler)

pipe = nixiepipe.pipe()

if len(sys.argv) > 1:
    symbols = sys.argv[1:len(sys.argv)]
    print symbols
else:
    symbols = ['^FTSE', '^FTAI', '^N225', '^GDAXI']

while(True): 
    for symbol in symbols:
        stock = Share(symbol)
        price = stock.get_price()
        change = stock.get_change()
        if price is not None:
            print symbol + ' Price: ' + price + ' Change: ' + change

            if float(change) >= 0:
                pipe.setColour(0,255,0)
            else:
                pipe.setColour(255,0,0)
            pipe.setNumber(float(price))
        else:
            print 'Symbol not found: ' + symbol
            pipe.setColour(255,255,255)
            pipe.setNumber(0)

        pipe.show()
        time.sleep(2)
