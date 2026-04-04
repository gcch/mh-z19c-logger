import datetime
import configparser
import socket
import time
import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS
from pyftdi.serialext import serial_for_url

# Config
config = configparser.ConfigParser()
CONFIG_FILE = "config.ini"
config.read(CONFIG_FILE, encoding="utf8")


def read_mhz19(port: str, retries: int = 3) -> dict:
    """Read CO2, temperature, and diagnostic data from MH-Z19 via UART."""
    CMD = b"\xff\x01\x86\x00\x00\x00\x00\x00\x79"
    resp = b""
    for attempt in range(retries):
        with serial_for_url(port, baudrate=9600, timeout=2) as ser:
            ser.reset_input_buffer()
            ser.reset_output_buffer()
            time.sleep(0.1)
            ser.write(CMD)
            resp = ser.read(9)
        if len(resp) == 9 and resp[0] == 0xFF and resp[1] == 0x86:
            break
        if attempt < retries - 1:
            time.sleep(1)
    else:
        raise ValueError(f"Invalid response after {retries} attempts: {resp.hex()}")
    checksum = (~sum(resp[1:8]) + 1) & 0xFF
    if checksum != resp[8]:
        raise ValueError("Checksum mismatch")
    return {
        "co2":         (resp[2] << 8) | resp[3],
        "temperature": resp[4] - 40,
        "TT":          resp[4],
        "SS":          resp[5],
        "UhUl":        (resp[6] << 8) | resp[7],
    }


def main():
    device_name = config.get("Device", "name",  fallback="mh_z19c")
    port        = config.get("Device", "port",  fallback="ftdi://ftdi:4232:1:1b/3")
    hostname    = socket.gethostname()

    data = read_mhz19(port)
    print(data)

    timestamp = int(datetime.datetime.now(datetime.timezone.utc).timestamp())
    df = {
        "_time": timestamp,
        "measurement": "env-sensor",
        "tags": {
            "client": hostname,
            "sensor": device_name,
        },
        "fields": {
            "co2":         int(data["co2"]),
            "temperature": float(data["temperature"]),
            "TT":          int(data["TT"]),
            "SS":          int(data["SS"]),
            "UhUl":        int(data["UhUl"]),
        },
    }

    url    = config.get("InfluxDB", "url",    fallback="")
    org    = config.get("InfluxDB", "org",    fallback="")
    token  = config.get("InfluxDB", "token",  fallback="")
    bucket = config.get("InfluxDB", "bucket", fallback="")

    client    = influxdb_client.InfluxDBClient(url, token)
    write_api = client.write_api(write_options=SYNCHRONOUS)
    write_api.write(bucket=bucket, org=org, record=df)


if __name__ == "__main__":
    main()
