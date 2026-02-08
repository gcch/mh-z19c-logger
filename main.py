import datetime
import configparser
import mh_z19
import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS

# config
config = configparser.ConfigParser()
CONFIG_FILE = "config.ini"
config.read(CONFIG_FILE, encoding="utf8")

def main():
    print("Hello from mh-z19c!")


    # Get data
    data = mh_z19.read_all(serial_console_untouched=True)
    print(data)

    timestamp = int(datetime.datetime.now(datetime.timezone.utc).timestamp())
    df = {
        '_time': timestamp,
        'measurement': 'env-sensor',
        'tags': { 
            'client': 'rpi3b',
            'sensor': 'mh-z19c'
        },
        'fields': {
            'co2': int(data['co2']),
            'temperature': float(data['temperature']),
            'TT': int(data['TT']),
            'SS': int(data['SS']),
            'UhUl': int(data['UhUl'])
        }
    }

    # Write to InfluxDB
    url = config.get("InfluxDB", "url", fallback="")
    org = config.get("InfluxDB", "org", fallback="")
    token = config.get("InfluxDB", "token", fallback="")
    bucket = config.get("InfluxDB", "bucket", fallback="")
    client = influxdb_client.InfluxDBClient(url, token)
    write_api = client.write_api(write_options=SYNCHRONOUS)
    write_api.write(bucket=bucket, org=org, record=df)

if __name__ == "__main__":
    main()
