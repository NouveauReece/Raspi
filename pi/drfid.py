import smbus2
import time

I2C_BUS = 1
USER_ADDRESS = 0x53
SYS_ADDRESS = 0x57

EOF_CHARACTER = 254

bus = smbus2.SMBus(I2C_BUS)

def read_bytes(address, reg, length):
    reg_high = (reg >> 8) & 0xFF
    reg_low = reg & 0xFF
    write = smbus2.i2c_msg.write(address, [reg_high, reg_low])
    read = smbus2.i2c_msg.read(address, length)
    bus.i2c_rdwr(write, read)
    return list(read)

def write_bytes(address, reg, data):
    reg_high = (reg >> 8) & 0xFF
    reg_low = reg & 0xFF
    msg = smbus2.i2c_msg.write(address, [reg_high, reg_low] + list(data))
    bus.i2c_rdwr(msg)

def read_user_memory(start=0x0000, length=256):
    return read_bytes(USER_ADDRESS, start, length)

def write_user_memory(data, start=0x0000):
    if start % 4 != 0:
        raise ValueError("Start address must be 4-byte aligned")
    data = list(data)
    while len(data) % 4 != 0:
        data.append(0x00)
    for i in range(0, len(data), 4):
        write_bytes(USER_ADDRESS, start + i, data[i:i+4])
        time.sleep(0.005)  # 5ms write cycle time

def drfid_read_string(start=0x0011, length=256):
    raw = read_user_memory(start, length)
    text = ''
    for b in raw:
        if b == EOF_CHARACTER:
            break
        text += chr(b)
    return text

def drfid_write_string(text, start=0x0000):
    data = [ord(c) for c in text] + [EOF_CHARACTER]
    write_user_memory(data, start)
