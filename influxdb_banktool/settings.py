import json
import os

CONF_PATH = os.path.expanduser("~/.influxdb-banktool/accounts.json")

with open(CONF_PATH) as f:
    config = json.load(f)
