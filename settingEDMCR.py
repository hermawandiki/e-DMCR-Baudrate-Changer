"""
e-DMCR Modbus Parameter

Default Setting: 38400 8N1
    - Baud Rate: 38400
    - Parity: None
    - Stop Bits: 1
    - Address: 1

Destination Setting: 9600 8N1
    - Baud Rate: 9600
    - Parity: None
    - Stop Bits: 1
    - Address: 1

Steps:
1. Connect with 38400 8N1
2. Enable configuration  -> Write 1 to address 0x1000/4097 (Configuration enabled)
3. Change baud rate code -> Write 0 to address 0x1002/4099 (Communication speed)
4. Disconnect and reconnect with 9600 8N1
5. Disable configuration -> Write 0 to address 0x1000/4097 (Configuration disabled)
6. Validate baud rate    -> Read address 0x1002/4099 (Communication speed)
7. Validate measurement  -> Read address 0x1300 to 0x1304 (Measurement table)

Baud rate code:
    - 0: 9600
    - 1: 19200
    - 2: 38400
    - 3: 57600
Configuration code:
    - 0: Disabled
    - 1: Enabled

for help : Diki Her (081235738756)    
"""

from pymodbus.client import ModbusSerialClient
from time import sleep

baudrate_int = int(input("Baudrate saiki  : "))
baudrate_dst = int(input("Baudrate tujuan : "))

def connect(baud):
    client = ModbusSerialClient(port="/dev/ttyACM0", baudrate=baud)
    if not client.connect():
        raise Exception("Ora kesambung kabel e...")
    return client

# Koneksi awal
try:
    client = connect(baudrate_int)
    print(f"1T. Wes connect karo baudrate {baudrate_int}")
except Exception as e:
    print(f"1F. Gak iso connect karo baudrate {baudrate_int} sebab {e}")
    raise SystemExit(1)

# Enable konfigurasi
try:
    r = client.write_register(0x1000, 1, slave=1)
    if r.isError():
        raise Exception(r)
    print("2T. Config wes di-enable")
except Exception as e:
    print(f"2F. Config gak iso di-enable sebab {e}")
    client.close()
    raise SystemExit(1)

# Ubah baud rate
baud_code = {9600: 0, 19200: 1, 38400: 2, 57600: 3}
val = baud_code[baudrate_dst]
try:
    r = client.write_register(0x1002, val, slave=1)
    if r.isError():
        raise Exception(r)
    print(f"3T. Baud rate wes diubah dadi {baudrate_dst}")
except Exception as e:
    print(f"3F. Baud rate gak iso diubah dadi {baudrate_dst} sebab {e}")
    client.close()
    raise SystemExit(1)

# Disconnect lan reconnect karo baud rate anyar
client.close()
sleep(1)

# Koneksi ulang karo baud rate anyar
try:
    client = connect(baudrate_dst)
    print(f"4T. Wes connect karo baudrate {baudrate_dst}")
except Exception as e:
    print(f"4F. Gak iso connect karo baudrate {baudrate_dst} sebab {e}")
    raise SystemExit(1)

# Disable konfigurasi
try:
    r = client.write_register(0x1000, 0, slave=1)
    if r.isError():
        raise Exception(r)
    print("5T. Config wes di-disable")
except Exception as e:
    print(f"5F. Config gak iso di-disable sebab {e}")
    client.close()
    raise SystemExit(1)

# Validasi baud rate
try:
    r = client.read_holding_registers(0x1002, count=1, slave=1)
    if r.isError():
        raise Exception(r)
    print(f"6T. Baud rate anyar: {r.registers[0]}")
except Exception as e:
    print(f"6F. Baud rate gak iso diubah sebab {e}")

# Validasi data measurement
try:
    r = client.read_holding_registers(0x1300, count=5, slave=1)
    if r.isError():
        raise Exception(r)
    print(f"7T. Data measurement: {r.registers}")
except Exception as e:
    print(f"7F. Data measurement gak iso diwaca sebab {e}")

client.close()
