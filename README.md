# Nixie Pipe Python Package

Python package containing *nixiepipe* class for interfacing with Nixie Pipe
Master hardware.

## Dependancies

* [pyserial](https://github.com/pyserial/pyserial).
* Nixie Pipe Master running [np-serial](https://github.com/tuna-f1sh/NixiePipe/tree/master/firmware/np-serial) firmware.
* _pyowm_, _configparser_, _threading_ _to use example scripts_.

## Install

In root folder, run  `./setup.py install`.

## Basic Usage

```python
import nixiepipe

# Create pipe object from nixiepipe class. Will auto find serial port using device descriptor
pipe = nixiepipe.pipe() 

pipe.setNumberUnits(0) # Set number of Nixie Pipe Unit modules
pipe.setColour(0,0,255) # Set array colour blue
pipe.setNumber(9999) # Set array number to 9999

# Write and show new settings
pipe.show()
```

## Examples 'examples/'

* **np-serial.py**: Basic API example showing for loop increment and colour
  set.
* **weather.py**: Display weather with Nixie Pipe Weather Unit Pipe using Open
  Weather Map.
* **cpu-usage.py**: Display CPU usage.
* **stock-ticker.py**: Display stock symbols. Pass symbols as arguments.

### Weather Example API Key Config File

You will need an API key for the Open Weather Map module. I have used
_configparser_ to save my API key outside the repo. To use the `weather.py`
you will need to **create a file 'owm-api.ini'** in the 'examples/' directory
with the contents:

```
[API]
OpenWeatherMap = YOUR_API_KEY
```
