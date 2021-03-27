from hashlib import sha256
from base64 import b64encode, b64decode
import json
import os

CACHE_PATH = os.path.expanduser('~/.influxdb-banktool/accounts_cache.json')

# Read details for item from cache.
# A hashed representation of item is used as cache key.
def cache_read(item):
    key = sha256(json.dumps(item, sort_keys=True).encode()).hexdigest()

    try:
        with open(CACHE_PATH, "r") as f:
            cache = json.load(f)

        b64data = cache[key]
        return b64decode(b64data)
    except:
        return None

# Write bytes-like data to cache, in base64 encoding.
# A hashed representation of item is used as cache key.
def cache_write(item, data):
    key = sha256(json.dumps(item, sort_keys=True).encode()).hexdigest()

    try:
        with open(CACHE_PATH, "r") as f:
            cache = json.load(f)
    except:
        cache = {}

    b64data = b64encode(data)
    cache[key] = b64data.decode()

    with open(CACHE_PATH, "w") as f:
       json.dump(cache, f)
