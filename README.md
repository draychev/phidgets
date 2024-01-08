# phidgets scripts

Here is how to build a Prometheus Dashboard showing the temperature and humidity in your home.

### Hardware
1. [Phidgets Humidity/Temperature Sensor](https://www.phidgets.com/?prodid=96) - the sensor that will measure temp and humidity
2. [PhidgetSBC4](https://www.phidgets.com/?prodid=969) - a Debian armhf running on a tiny Allwinner A20 	Dual-Core ARM Cortex-A7

### Python packages
 - `flask`
 - `prometheus_client`
 - `Phidget22`

### Run it
The `prom.py` file stitches the Promethous gauge and the Phidgets libraries. This exposes a `/metrics` endpoint from where a Prometheus server can scrape metrics.

### Prometheus
- Show a graph of `humidity_gauge{symbol="%"}`
- Show a graph of `temp_gauge{symbol="°C"}`
