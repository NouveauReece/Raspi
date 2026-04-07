import smbus2
import time

I2C_BUS = 1
USER_ADDRESS = 0x53
SYS_ADDRESS = 0x57

EOF_CHARACTER = 254

bus = smbus2.SMBus(I2C_BUS)

# --- Low level ---

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

# --- Security ---

def present_i2c_password():
    """Present default all-zero I2C password to open security session"""
    password = [0x00] * 8
    # Format: [0x09, 0x00] + 8 pwd bytes + [0x09] + 8 pwd bytes
    payload = [0x09, 0x00] + password + [0x09] + password
    msg = smbus2.i2c_msg.write(SYS_ADDRESS, payload)
    bus.i2c_rdwr(msg)

# --- GPO ---

def enable_gpo_rf_write():
    """Enable GPO pulse on RF write. Must call present_i2c_password() first."""
    # GPO register at 0x0000 in system area
    # bit 7 = GPO_EN, bit 2 = RF_WRITE
    write_bytes(SYS_ADDRESS, 0x0000, [0x84])

# --- User memory ---

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

# --- Setup ---

def drfid_setup():
    present_i2c_password()
    enable_gpo_rf_write()
    print("ST25DV GPO configured for RF write interrupt")
