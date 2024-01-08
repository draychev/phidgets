# Measure Humidity and Temperature of your home with Phidgets and Prometheus

Here is how to build a Prometheus Dashboard showing the temperature and humidity in your home, leveraging [Phidgets](https://www.phidgets.com/) and a box running Debian.

### Hardware
1. [Phidgets Humidity/Temperature Sensor](https://www.phidgets.com/?prodid=96) - the sensor that will measure temperature and humidity
2. [PhidgetSBC4](https://www.phidgets.com/?prodid=969) - an armhf [Debian Bullseye](https://www.debian.org/releases/bullseye/) running on a tiny [Allwinner A20](https://linux-sunxi.org/A20)	Dual-Core ARM Cortex-A7

### Python packages
 - `flask`
 - `prometheus_client`
 - `Phidget22`

### Run
The `prom.py` file stitches the Promethous gauge and the Phidgets libraries. This exposes a `/metrics` endpoint from where a Prometheus server can scrape metrics.

### Prometheus
[Prometheus](https://prometheus.io/docs/introduction/overview/) is a free software application used for event monitoring and alerting. Install it on a server (more powerful than the Phidgets SBC), which is on the same network (tailscale) as your Phidgets SBC. This machine will be performing periodic HTTP GET calls to the Phidgets SBC box.

1. [Install Prometheus](https://prometheus.io/docs/prometheus/latest/installation/)
2. Configure it:
```sh
$ cat /etc/prometheus/prometheus.yml
```

```yaml
# my global config
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  # The job name is added as a label `job=<job_name>` to any timeseries scraped from this config.
  - job_name: "prometheus"

    # metrics_path defaults to '/metrics'
    # scheme defaults to 'http'.
    # in targets - add the IP address of the Phidgets SBC4 box
    static_configs:
      - targets:
        - 1xx.2xx.3xx.4x:5000
```
4. Connect to the Prometheus server: http://your-prometheus-server:9090/
5. Query for Humidity and Temperature
- Show a graph of `humidity_gauge{symbol="%"}` ![prom-humidity](https://github.com/draychev/phidgets/assets/49918230/d8269610-cf66-4790-82fa-9d4ac7eba61e)
- Show a graph of `temp_gauge{symbol="°C"}` ![prom-temperature](https://github.com/draychev/phidgets/assets/49918230/8b9b7e78-68cd-40c7-9e40-49e9bb3fa8ae)
