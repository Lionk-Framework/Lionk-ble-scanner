#!/usr/bin/env python3
import asyncio
from typing import Callable
from bleak import BleakClient, BleakScanner
from bleak.backends.device import BLEDevice
from bleak.backends.characteristic import BleakGATTCharacteristic
from dataclasses import dataclass
from typing import Awaitable, Union

from bleak.backends.scanner import AdvertisementData

DEVICE_NAME_PREFIX = "Lionk"

TEMP_DEVICE_NAME_PREFIX = f"{DEVICE_NAME_PREFIX}-Temp"
TEMP_DEVICE_VERSION_UUID = "00000006-7669-6163-616d-2d63616c6563"
TEMP_DEVICE_DATA_UUID = "00000008-7669-6163-616d-2d63616c6563"


@dataclass
class DeviceInfo:
    notification_uuids: list[
        tuple[
            str,
            Callable[
                [BleakGATTCharacteristic, bytearray], Union[None, Awaitable[None]]
            ],
        ]
    ]
    version_uuid: str


def temp_device_data_handler(
    characteristic: BleakGATTCharacteristic, data: bytearray
) -> None:
    """Handle incoming notifications from the BLE device."""

    if characteristic.uuid != TEMP_DEVICE_DATA_UUID:
        print(f"Unknown characteristic uuid ({characteristic.uuid})")
    version = data[0]
    temperature = (data[1] << 8 | data[2]) / 10
    battery_mv = data[3] << 8 | data[4]

    print(f"v{version} {temperature}°C {battery_mv}mV")


TEMP_DEVICE_INFO = DeviceInfo(
    notification_uuids=[(TEMP_DEVICE_DATA_UUID, temp_device_data_handler)],
    version_uuid=TEMP_DEVICE_DATA_UUID,
)


def get_device_info(device: BLEDevice) -> DeviceInfo | None:
    if not device.name:
        return None

    if device.name.startswith(TEMP_DEVICE_NAME_PREFIX):
        return TEMP_DEVICE_INFO

    return None


connected_devices: set[str] = set()


def filter_devices(_: BLEDevice, adv_data: AdvertisementData) -> bool:
    if not adv_data.local_name:
        return False
    return (
        adv_data.local_name.startswith(DEVICE_NAME_PREFIX)
        and adv_data.local_name not in connected_devices
    )


async def handle_device(device: BLEDevice, device_info: DeviceInfo):

    assert device.name

    print(f"Connected to {device.name}")
    try:
        async with BleakClient(device) as client:

            for service in client.services:
                print(f"Service: {service.uuid}")
                for char in service.characteristics:
                    print(
                        f"  Characteristic: {char.uuid}, Properties: {char.properties}"
                    )

            notification_lst = []
            for characteristic in device_info.notification_uuids:
                uuid = characteristic[0]
                cb = characteristic[1]

                characteristic = client.services.get_characteristic(uuid)
                if not characteristic:
                    print(f"Couldn't find characteristic by {uuid}")
                    continue

                props = characteristic.properties
                if "notify" not in props and "indicate" not in props:
                    print(
                        f"Warning: Characteristic with {uuid} doesn't support notifications"
                    )
                    print(f"Available properties: {props}")
                    continue
                await client.start_notify(uuid, cb)
                print(f"Subscribed to {uuid} successfully!")
                notification_lst.append(uuid)

            print("Waiting for notifications. Press Ctrl+C to exit...")
            try:
                await asyncio.Future()
            except asyncio.CancelledError:
                # This will catch Ctrl+C
                pass
            finally:
                for uuid in notification_lst:
                    await client.stop_notify(uuid)
                connected_devices.remove(device.name)
                return

    except Exception as e:
        print(f"Error: {e}")


async def scan_devices():
    print(f"Scanning for BLE device starting with {DEVICE_NAME_PREFIX}")

    while True:
        device = await BleakScanner.find_device_by_filter(filter_devices)

        if device is None:
            if len(connected_devices) == 0:
                print(f"Could not find any device with name: {DEVICE_NAME_PREFIX}")
                devices = await BleakScanner.discover()
                print("Available devices:")
                for d in devices:
                    print(f"  {d.name}: {d.address}")

            try:
                await asyncio.sleep(5.0)
            except asyncio.CancelledError:
                return
            continue

        device_info = get_device_info(device)
        if not device_info:
            print(
                f"Couldn't get necessary info to handle this device ({device.address} - {device.name})"
            )
            continue

        if not device.name:
            continue
        connected_devices.add(device.name)
        asyncio.create_task(handle_device(device, device_info))


if __name__ == "__main__":
    asyncio.run(scan_devices())
