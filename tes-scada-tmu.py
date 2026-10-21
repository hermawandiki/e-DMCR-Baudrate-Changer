import struct
import time
import os
from pymodbus.client import ModbusTcpClient

TMU_IP   = input("IP TMU   : ")
TMU_PORT = input("Port TMU : ")

REGISTER_MAP = [
    (1,  "A-N Phase Voltage",       "Va",     0,  "U32", 10),
    (2,  "B-N Phase Voltage",       "Vb",     2,  "U32", 10),
    (3,  "C-N Phase Voltage",       "Vc",     4,  "U32", 10),
    (4,  "A-B Phase Voltage",       "Vab",    6,  "U32", 10),
    (5,  "B-C Phase Voltage",       "Vbc",    8,  "U32", 10),
    (6,  "A-C Phase Voltage",       "Vac",    10, "U32", 10),
    (7,  "A Phase Current",         "Ia",     12, "U16", 10),
    (8,  "B Phase Current",         "Ib",     13, "U16", 10),
    (9,  "C Phase Current",         "Ic",     14, "U16", 10),
    (10, "Current Average",         "Iavg",   15, "U16", 10),
    (11, "Neutral Current",         "In",     16, "U16", 10),
    (12, "THD V1",                  None,     17, "U16", 100),
    (13, "THD V2",                  None,     18, "U16", 100),
    (14, "THD V3",                  None,     19, "U16", 100),
    (15, "THD I1",                  None,     20, "U16", 100),
    (16, "THD I2",                  None,     21, "U16", 100),
    (17, "THD I3",                  None,     22, "U16", 100),
    (18, "Phase A Active Power",    "Pa",     23, "S32", 1),
    (19, "Phase B Active Power",    "Pb",     25, "S32", 1),
    (20, "Phase C Active Power",    "Pc",     27, "S32", 1),
    (21, "Total Active Power",      "Psig",   29, "S32", 1),
    (22, "Phase A Reactive Power",  "Qa",     31, "S32", 1),
    (23, "Phase B Reactive Power",  "Qb",     33, "S32", 1),
    (24, "Phase C Reactive Power",  "Qc",     35, "S32", 1),
    (25, "Total Reactive Power",    "Qsig",   37, "S32", 1),
    (26, "Phase A Apparent Power",  "Sa",     39, "U32", 1),
    (27, "Phase B Apparent Power",  "Sb",     41, "U32", 1),
    (28, "Phase C Apparent Power",  "Sc",     43, "U32", 1),
    (29, "Total Apparent Power",    "Ssig",   45, "U32", 1),
    (30, "Phase A Power Factor",    "PFa",    47, "U16", 1000),
    (31, "Phase B Power Factor",    "PFb",    48, "U16", 1000),
    (32, "Phase C Power Factor",    "PFc",    49, "U16", 1000),
    (33, "Total Power Factor",      "PFsig",  50, "U16", 1000),
    (34, "Frequency",               "Freq",   51, "U16", 100),
    (35, "kWh",                     "kWh",    52, "U32", 1),
    (36, "kVARh",                   "kVARh",  54, "U32", 1),
    (37, "Busbar Temp A",           "Busbar A",     56, "U16", 100),
    (38, "Busbar Temp B",           "Busbar B",     57, "U16", 100),
    (39, "Busbar Temp C",           "Busbar C",     58, "U16", 100),
    (40, "Oil Temperature",         "Temp",   59, "U16", 100),
    (41, "A Phase WTI",             "WTIa",   60, "U16", 100),
    (42, "B Phase WTI",             "WTIb",   61, "U16", 100),
    (43, "C Phase WTI",             "WTIc",   62, "U16", 100),
    (44, "Pressure Tank",           "Press",  63, "S16", 1000),
    (45, "Level Oil",               "Level",  64, "U16", 1),
    (46, "Krated A",                None,     65, "U16", 1),
    (47, "Derated A",               None,     66, "U16", 100),
    (48, "Krated B",                None,     67, "U16", 1),
    (49, "Derated B",               None,     68, "U16", 100),
    (50, "Krated C",                None,     69, "U16", 1),
    (51, "Derated C",               None,     70, "U16", 100),
    (52, "H2 ppm",                  None,     71, "U16", 1),
    (53, "Moisture",                None,     72, "U16", 1),
    (54, "Gap UV",                  None,     73, "U32", 10),
    (55, "Gap VW",                  None,     75, "U32", 10),
    (56, "Gap UW",                  None,     77, "U32", 10),
    (57, "Efficiency",              None,     80, "U16", 100),
]

def decode_value(registers, offset, dtype):
    if dtype == "U16":
        return registers[offset]
    elif dtype == "S16":
        raw16 = registers[offset]
        return struct.unpack(">h", struct.pack(">H", raw16))[0]

    lo = registers[offset]
    hi = registers[offset + 1]
    raw = (hi << 16) | lo

    if dtype == "U32":
        return raw
    elif dtype == "S32":
        return struct.unpack(">i", struct.pack(">I", raw))[0]
    else:
        raise ValueError(f"Tipe data tidak dikenal: {dtype}")

def read_tmu_data(client):
    result = client.read_holding_registers(0, count=81, device_id=1)

    if result.isError():
        raise ConnectionError(f"Gagal membaca register Modbus: {result}")

    regs = result.registers
    data = {}

    for no, name, symbol, addr, dtype, gain in REGISTER_MAP:
        offset = addr - 0
        raw_value = decode_value(regs, offset, dtype)
        scaled_value = raw_value / gain if gain != 1 else raw_value
        key = symbol if symbol else name
        data[key] = scaled_value
    return data

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

def print_grid(data, columns=4, cell_width=22):
    items = list(data.items())
    total = len(items)
    rows = (total + columns - 1) // columns

    border = "+" + ("-" * cell_width + "+") * columns
    print(border)

    for r in range(rows):
        line = "|"
        for c in range(columns):
            idx = c * rows + r
            if idx < total:
                key, val = items[idx]
                if isinstance(val, float):
                    val_str = f"{val:.2f}"
                else:
                    val_str = str(val)
                cell = f"{key}: {val_str}"
            else:
                cell = ""
            line += cell[:cell_width].ljust(cell_width) + "|"
        print(line)
    print(border)

def connect_with_retry(client):
    while True:
        if client.connect():
            return
        clear_screen()
        print(f"Gagal connect ke {TMU_IP}:{TMU_PORT}, "
              f"retry dalam 3s...  ({time.strftime('%H:%M:%S')})")
        time.sleep(3)

def main():
    client = ModbusTcpClient(TMU_IP, port=TMU_PORT)
    connect_with_retry(client)
    try:
        while True:
            if not client.is_socket_open():
                client.close()
                connect_with_retry(client)
            try:
                data = read_tmu_data(client)
                clear_screen()
                print(f"TMU Live Monitor  |  {TMU_IP}:{TMU_PORT}  |  {time.strftime('%H:%M:%S')}")
                print_grid(data)
            except ConnectionError as e:
                clear_screen()
                print(f"[{time.strftime('%H:%M:%S')}] {e}")
                print("Koneksi bermasalah, mencoba reconnect...")
                client.close()
                connect_with_retry(client)
                continue
            time.sleep(2)
    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        client.close()

if __name__ == "__main__":
    main()