# -*- encoding: utf-8 -*-

"""
Sensors:
* BME280: weather (temperature, pressure, relative humidity)
* LTR-559: light and proximity
* MICS6814: gas
* PMS5003: particulate matter

Additional components:
* MEMS microphone
* 0.96" colour LCD (160x80)
* ADS1015 analog to digital converter
"""

from flask import Flask, Response
from waitress import serve
from prometheus_client import Gauge, generate_latest
from smbus2 import SMBus
from bme280 import BME280 # pimoroni-bme280 on PyPi
from ltr559 import LTR559
from pms5003 import PMS5003
from enviroplus import gas
from enviroplus.noise import Noise

# QNH is an altimeter setting --- "the value of the atmospheric
# presure used to adjust the sub-scale of a pressure altimeter
# so that it indicates the height of an aircraft above a known
# reference surface" according to the Wikipedia article on
# "Altimeter setting". I've configured this to the value for
# Melbourne according to the Australian Bureau of Meterology.
LOCAL_QNH = 1008

app = Flask(__name__)


# Weather
#
# Gauges technically spport a "unit" argument, but this is
# appended onto the gauge name. With units like "°C" this makes
# the gauge name invalid. So I'll keep the units in the
# descriptions instead.
temperature = Gauge("temperature", "temperature in °C")
humidity = Gauge("humidity", "humidity as a percentage")
pressure = Gauge("pressure", "pressure in hPa")
altitude = Gauge("altitude", "altitude in metres above sea level")

bus = SMBus(1)
bme280 = BME280(i2c_dev=bus)

def update_weather():
    temperature.set(bme280.get_temperature())
    humidity.set(bme280.get_humidity())
    pressure.set(bme280.get_pressure())
    altitude.set(bme280.get_altitude(qnh=LOCAL_QNH))

# Light
#
# There's also a proximity sensing capacity here, available
# through ltr559.get_proximity(). I don't have a use for this.

light = Gauge("light", "light in lux")
ltr559_measure = LTR559()

def update_light():
    ltr559_measure.update_sensor()
    light.set(ltr559_measure.get_lux())
    
# Gas

reducing = Gauge("reducing", "reducing gases in Ohms")
oxidising = Gauge("oxidising", "oxidising gases in Ohms")
ammonia = Gauge("ammonia", "ammonia in Ohms")

def update_gas():
    mixture = gas.read_all()
    reducing.set(mixture.reducing)
    oxidising.set(mixture.oxidising)
    ammonia.set(mixture.nh3)

# Noise
#
# Noise is measured in different frequency groups. The default uses 3:
# low, mid and high, and a total which is actually the average of all 3.
noise = Gauge("noise", "noise in amps", ["level"])

noise_measure = Noise()
# This takes a little longer --- by default listens for 0.5 seconds
def update_noise():
    amp_low, amp_mid, amp_high, amp_total = noise_measure.get_noise_profile()
    noise.labels(level="low").set(amp_low)
    noise.labels(level="mid").set(amp_mid)
    noise.labels(level="high").set(amp_high)
    noise.labels(level="total").set(amp_total)

# Particulates
#
# This sensor also allows for measuring a variant "atmospheric environment".
# It's not clear to me what this means, so I'm sticking to the code as
# used in the examples in the module Github repository.
pms5003_measure = PMS5003()
particulates = Gauge("particulates", "particulates in µg/m³", ["diameter"])

def update_particulates():
    data = pms5003_measure.read()
    particulates.labels(diameter="1.0").set(data.pm_ug_per_m3(1.0))
    particulates.labels(diameter="2.5").set(data.pm_ug_per_m3(2.5))
    particulates.labels(diameter="10").set(data.pm_ug_per_m3(10))


@app.route("/metrics", methods=["GET"])
def return_metrics():
    update_weather()
    update_light()
    update_noise()
    update_gas()
    update_particulates()
    
    return Response(
        generate_latest(),
        mimetype="text/plain; charset=utf-8"
    )

# Port 80 is protected, but I don't want to use sudo. Instead, I followed:
# gist.gitub.com/justinmlam/f13bb53be9bb15ec182b4877c9e9958d
# Then run the app with authbind --deep python3 environment.py
   
if __name__ == "__main__":
    serve(app, host="0.0.0.0", port=80)

