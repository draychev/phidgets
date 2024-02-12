#!/usr/bin/env python3

import os
import sys
import time
import subprocess
import re
import threading

from flask import Flask, jsonify, request
from prometheus_client import make_wsgi_app, Counter, Histogram, Gauge
from werkzeug.middleware.dispatcher import DispatcherMiddleware

loc = os.environ.get("LOCATION")
if loc is not None:
    print("LOCATION:", loc)
else:
    print("LOCATION env var is not set. Create .env and add 'export LOCATION=xyz'")
    sys.exit(1)

system_info = os.uname()
computer_name = system_info.nodename

app = Flask(__name__)

app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {
    '/metrics': make_wsgi_app()
})

labels = [loc]

PING_GAUGE = Gauge('ping_gauge', 'Ping', ['name', 'location', 'destination'])
PING_HIST = Histogram('ping_histogram', 'Ping', ['name', 'location', 'destination'])

@app.route('/')
def index():
    return redirect('/metrics')

def ping_and_get_time(destinationHost):
    # Execute the ping command
    command = ['ping', '-c', '1', destinationHost]
    try:
        output = subprocess.check_output(command, universal_newlines=True)

        # Use regex to find the time value in the output
        match = re.search(r'time=(\d+\.?\d*) ms', output)
        if match:
            # Return the time in milliseconds
            return float(match.group(1))
        else:
            print(f"Time not found in ping output: {output}")
            return 0
    except subprocess.CalledProcessError as e:
        print(f"Failed to execute ping: {str(e)}")
        return 0

def ping_every_5_seconds():
    while True:
        ### First measure ping to 8.8.8.8
        destinationHost = '8.8.8.8'
        ping_time = ping_and_get_time(destinationHost)
        PING_HIST.labels(computer_name, loc, destinationHost).observe(ping_time)
        PING_GAUGE.labels(computer_name, loc, destinationHost).set(ping_time)

        ### Then measure ping to sz.inetg.bg
        destinationHost = 'sz.inetg.bg'
        ping_time = ping_and_get_time(destinationHost)
        PING_HIST.labels(computer_name, loc, destinationHost).observe(ping_time)
        PING_GAUGE.labels(computer_name, loc, destinationHost).set(ping_time)

        time.sleep(5)

if __name__ == '__main__':
    # Create a thread that runs the ping_every_5_seconds() function
    thread = threading.Thread(target=ping_every_5_seconds)
    # Daemon threads automatically shut down when the main program exits
    thread.daemon = True
    thread.start()

    app.run(host='0.0.0.0', port=5000)
