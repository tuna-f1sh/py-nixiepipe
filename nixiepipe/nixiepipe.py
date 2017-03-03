# encoding: utf-8
# /*
# //  GPL 3.0 License

# //  Copyright (c) 2016 John Whittington www.jbrengineering.co.uk

# //  This program is free software: you can redistribute it and/or modify
# //     it under the terms of the GNU General Public License as published by
# //     the Free Software Foundation, either version 3 of the License, or
# //     (at your option) any later version.

# //     This program is distributed in the hope that it will be useful,
# //     but WITHOUT ANY WARRANTY; without even the implied warranty of
# //     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# //     GNU General Public License for more details.

# //     You should have received a copy of the GNU General Public License
# //     along with this program.  If not, see <http:www.gnu.org/licenses/>.
# */

"""
Nixie Pipe module for interacing with the Nixie Pipe Master. Slave modules can be connected to form Nixie Pipe array that can display numbers larger then 9 and/or symbols

Examples:
    Basic usage::
        import nixiepipe

        pipes = nixiepipe.pipe() # auto find serial port using device descriptor

        pipe.setNumber(9) # set pipe to display 9
        pipe.setColour(0,255,0) # set pipe green
        pipe.show() # write and show changes

Classes:
    pipe: Nixie Pipe Master object, which controls Nixie Pipe Slaves.
"""

import serial
from serial.tools import list_ports
import time

PIPEBAUD = 57600

def _findPipePort():
    """Auto find Nixie Pipe port using device descriptor"""

    ports = list(list_ports.grep("Nixie Pipe"))
    if len(ports) < 1:
        raise RuntimeError('No Nixie Pipe Master module detected!')
    elif len(ports) > 1:
        for x in range(len(ports)):
            print x, ":", ports[x][0]
        idx = int(raw_input("Which Nixie Pipe Master port? Enter list number\n> "))
        return ports[idx][0]
    else:
        return ports[0][0]

class pipe:
    """Nixie Pipe class
    
    Args:
        port (str): Port Nixie Pipe is connected to. Defaults to autofind using USB device descriptors.
    """

    # Nixie Pipe command dictionary
    _commands = {
            "setNumber" : 0x40,
            "setPipeNumber" : 0x41,
            "setColour" : 0x42,
            "setPipeColour" : 0x43,
            "brightness" : 0x44,
            "clear" : 0x45,
            "clearPipe" : 0x46,
            "getNumber" : 0x47,
            "connect" : 0x48,
            "setNumberUnits" : 0x49,
            "show" : 0x50,
    }
    _units = {
            "Volts" : 0,
            "Amps" : 1,
            "Watts" : 2,
            "Grams" : 3,
            "Hertz": 4,
            "Celsius" : 5,
            "Newtons" : 6,
            "Meters" : 7,
            "Seconds" : 8,
            "Ohm" : 9,
    }
    _prefix = {
            "Pico" : 0,
            "Nano" : 1,
            "Micro" : 2,
            "Milli" : 3,
            "Kila": 4,
            "Mega" : 5,
            "Giga" : 6,
            "Tera" : 7,
            "Neg" : 8,
            "Pos" : 9,
    }
    _weather = {
            "Sun" : 0,
            "Sunny" : 0,
            "01d" : 0,
            "01n" : 0,
            "Rain" : 1,
            "Rainy" : 1,
            "09d" : 1,
            "09n" : 1,
            "10d" : 1,
            "10n" : 1,
            "Cloud" : 2,
            "Clouds" : 2,
            "03d" : 2,
            "03n" : 2,
            "SunCloud" : 3,
            "Broken clouds" : 3,
            "02d" : 3,
            "02n" : 3,
            "04d" : 3,
            "04n" : 3,
            "Snow" : 4,
            "Snowy" : 4,
            "13d" : 4,
            "13n" : 4,
            "Wind" : 5,
            "Windy" : 5,
            "Storm" : 6,
            "Stormy" : 6,
            "11d" : 6,
            "11n" : 6,
            "Fog" : 7,
            "Haze" : 7,
            "Mist" : 7,
            "Foggy" : 7,
            "50d" : 7,
            "50n" : 7,
            "Percent" : 8,
            "Pascal" : 9,
    }

    def __init__(self,port = 0, debug = False):
        """Find and create serial object then issue connect command and await confirmation"""

        self.debug = debug

        if port == 0:
            port = _findPipePort()
        self.ser = serial.Serial(port,PIPEBAUD,timeout=1)
        # Wait for boot
        time.sleep(0.1)

        # Flush serial in case of junk
        self.ser.flush()
        # Send connect
        version = self.connect()
        if version >= 0:
            print 'Connected to Nixie Pipe version ' + str(version)
        else:
            self.close()
            raise RuntimeError('Could not connect to Nixie Pipe!')

    def close(self):
        """Delete and close serial object associated with Nixie Pipe"""

        self.ser.close()

    def _sendCommand(self, command, message, size):
        """Send command and message packet to Nixie Pipe"""

        # packet is size of message plus two bytes for header
        packet = [0] * (size + 2)
        # size is first byte
        packet[0] = size & 0xFF
        # command is second byte
        packet[1] = command & 0xFF
        # append the message
        if size > 1:
            packet[2:2+size] = message
        else:
            packet[2] = message

        if self.debug:
            print packet
        # write packet
	packet = bytearray(packet)
        self.ser.write(packet)

    def _getResponce(self, length):
        """Get response packet from Nixie Pipe following command

        Args:
            length (int): Length of expected return message (bytes)
        
        """

        res = self.ser.read(length+2)
        res = list(bytearray(res))

        if self.debug:
            print res
        
        return res

    def _valueToMessage(self,value):
        """Convert uint32 to message bytes"""

        message = [0] * 4
        message[0] = value & 0xFF
        message[1] = (value >> 8) & 0xFF
        message[2] = (value >> 16) & 0xFF
        message[3] = (value >> 24) & 0xFF

        return message

    def _messageToValue(self,message):
        """Convert message packet to uint32"""
        
        value = 0 

        for x in range(0,3):
            value += (message[x] & 0xFF) << (8 * x)

        return value

    def connect(self):
        """Connect to the Nixie Pipe Master. Used by class initialiser to confirm Nixie Pipe connected
        
        Returns:
            Firmware version number (float) if connection sucessful, otherwise -1.
        """

        self._sendCommand(self._commands["connect"],[0x4E, 0x50],2)
        res = self._getResponce(2)

        version = -1
        if len(res) == 4:
            if (res[1] == self._commands["connect"]):
                major = res[3]
                minor = res[2]
                version = str(major) + '.' + str(minor)

        return float(version)

    def setNumber(self,value):
        """Set Nixie Pipe array number

        Args:
            value (int): Number to set; auto decimates (value) to pipes.
        """

        value = int(round(value)) # can only print ints
        self._sendCommand(self._commands["setNumber"],self._valueToMessage(value),4)
        res = self._getResponce(1)

    def setPipeNumber(self,pipe,value):
        """Set individual Nixie Pipe number

        Args:
            pipe (int): Pipe to set.
            value (int): Value to set (<10).
        """

        value = int(round(value)) # can only print ints
        self._sendCommand(self._commands["setPipeNumber"],[pipe, value],2)
        res = self._getResponce(1)

    def setColour(self,r,g,b):
        """Set global Nixie Pipe array colour using RGB colour coding

        Args:
            r (byte): Red saturation.
            g (byte): Red saturation.
            b (byte): Red saturation.
        """

        # sanity check arguments are bytes
        r &= 0xFF
        g &= 0xFF
        b &= 0xFF
        self._sendCommand(self._commands["setColour"],[r, g, b],3)
        res = self._getResponce(1)

    def setPipeColour(self,pipe,r,g,b):
        """Set individual (pipe) Nixie Pipe colour using (r) (g) (b) colour coding"""

        # sanity check arguments are bytes
        r &= 0xFF
        g &= 0xFF
        b &= 0xFF
        self._sendCommand(self._commands["setPipeColour"],[pipe,r, g, b],4)
        res = self._getResponce(1)

    def clear(self):
        """Clear Nixie Pipe array (set black)"""

        self._sendCommand(self._commands["clear"],1,1)
        res = self._getResponce(1)
    
    def clearPipe(self,pipe):
        """Clear individual (pipe) Nixie Pipe (set black)"""

        self._sendCommand(self._commands["clearPipe"],pipe & 0xFF,1)
        res = self._getResponce(1)

    def setBrightness(self, value):
        """Set Nixie Pipe array brightness (off) 0-255 (bright)"""
        
        self._sendCommand(self._commands["brightness"],value & 0xFF,1)
        res = self._getResponce(1)

    def setNumberUnits(self, value):
        """Set number of Nixie Pipe unit modules. Units offset the array number so they can be set individually."""

        self._sendCommand(self._commands["setNumberUnits"],value & 0xFF,1)
        res = self._getResponce(1)

    def getNumber(self):
        """Get current number being displayed (int)."""

        self._sendCommand(self._commands["getNumber"],1,1)
        res = self._getResponce(4)

        if (len(res) == 6):
            return self._messageToValue(res[2:5])
        else:
            return -1

    def setWeather(self, pipe, symbol):
        """Set Nixie Pipe Weather unit (pipe) with (symbol). 
        
        Args:
            symbol (str): A string corresponding to the icon to set or Open Weather Map iocon code.
        """
        
        symbol = symbol.capitalize()

        index = self._weather[symbol]
        
        self.setPipeNumber(pipe,index)

    def show(self):
        """Write and show changes to Nixie Pipe array
        
        Must be called after setting commands to view changes. Call disables interrupts to write LEDs so a delay is inforced by waiting for the responce.
        """

        self._sendCommand(self._commands["show"],1,1)
        # give time for FastLED during which interrupts disabled and so serial will be ignored
        res = self._getResponce(1)
