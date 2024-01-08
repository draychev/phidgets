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
1. Install prometheus
2. Configure it:
```sh
$ cat /etc/prometheus/prometheus.yml
```

```yaml
# my global config
global:
  scrape_interval: 15s # Set the scrape interval to every 15 seconds. Default is every 1 minute.
  evaluation_interval: 15s # Evaluate rules every 15 seconds. The default is every 1 minute.
  # scrape_timeout is set to the global default (10s).

# Alertmanager configuration
alerting:
  alertmanagers:
    - static_configs:
        - targets:
          # - alertmanager:9093

# Load rules once and periodically evaluate them according to the global 'evaluation_interval'.
rule_files:
  # - "first_rules.yml"
  # - "second_rules.yml"

# A scrape configuration containing exactly one endpoint to scrape:
# Here it's Prometheus itself.
scrape_configs:
  # The job name is added as a label `job=<job_name>` to any timeseries scraped from this config.
  - job_name: "prometheus"

    # metrics_path defaults to '/metrics'
    # scheme defaults to 'http'.

    static_configs:
      - targets:
        - 1xx.2xx.3xx.4x:5000
```

4. Query
- Show a graph of `humidity_gauge{symbol="%"}` ![prom-humidity](https://github.com/draychev/phidgets/assets/49918230/d8269610-cf66-4790-82fa-9d4ac7eba61e)
- Show a graph of `temp_gauge{symbol="°C"}` ![prom-temperature](https://github.com/draychev/phidgets/assets/49918230/8b9b7e78-68cd-40c7-9e40-49e9bb3fa8ae)
