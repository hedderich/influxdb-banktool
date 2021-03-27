from datetime import datetime


def parse_influxdb_timestamp(timestamp):
    return datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ")
