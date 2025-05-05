# Lionk BLE Scanner

A simple Proof-of-Concept (POC) BLE scanner written in Python. This script scans for Lionk BLE devices using the Bluetooth Low Energy protocol.

# Features

- Scans for nearby Lionk BLE devices
- Outputs device information to the console
- Lightweight and easy to run

# Supported devices

- [Lionk BLE nRF Temperature Sensor](https://github.com/Lionk-Framework/Lionk-nrf-temperature)

# Requirements

- Python 3.13.3 (tested on Linux)
- Dependencies listed in requirements.txt

# Quick start

## Docker (Linux only)

1. Use the provided docker image to run the scanner with BLE access

> [!NOTE]
> BLE access requires mapping the system D-Bus socket into the container.

```bash
docker run -v /var/run/dbus:/var/run/dbus ghcr.io/lionk-framework/lionk-ble-scanner:main
```

## Python

1. Clone the repository

```bash
git clone https://github.com/yourusername/lionk-ble-scanner.git
cd lionk-ble-scanner
```

2. Create a virtual environment (optional but recommended)

```bash
python3 -m venv env
source env/bin/activate
```

3. Install dependencies

```bash
pip install -r requirements.txt
```

4. Run the scanner

```bash
python ble_scanner.py
```
> [!NOTE]  
>  This was tested using Python 3.13.3 on a Linux machine. Compatibility with other versions or operating systems is not guaranteed.


# License

This project is licensed under the [MIT License](./LICENSE)
