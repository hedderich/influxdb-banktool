# influxdb-banktool

Create influxdb time series from fints response data, e.g. to plot neat graphs
with Grafana.

<img src="https://raw.githubusercontent.com/hedderich/influxdb-banktool/master/example.png" alt="Example balance displayed in Grafana" height="280" />

## Setup

Clone repository and execute

```
python setup.py install
```

or just install directly via pip:

```
pip install git+git://github.com/hedderich/influxdb-banktool.git
```

Create a config file with your influxdb connection and your FinTS credentials, using `config.json` as a reference
```
mkdir $HOME/.influxdb-banktool
vi $HOME/.influxdb-banktool/accounts.json
```

## Usage

```
influxdb-banktool
```
