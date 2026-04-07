from mfrc522 import MFRC522
import RPi.GPIO as GPIO
import time

READ_BUF_LEN = 18
EOF_CHARACTER = 254

reader = MFRC522()

def read_ntag_page(page):
    recvData = [0x30, page]
    pOut = reader.CalulateCRC(recvData)
    recvData += pOut
    (status, backData, backLen) = reader.MFRC522_ToCard(reader.PCD_TRANSCEIVE, recvData)
    if status == reader.MI_OK and len(backData) >= 4:
        return backData[:16]
    return None

def select_ntag():
    reader.Write_MFRC522(reader.BitFramingReg, 0x00)
    (status, backData, _) = reader.MFRC522_ToCard(
        reader.PCD_TRANSCEIVE, [0x93, 0x20]
    )
    if status != reader.MI_OK or len(backData) < 5:
        return None

    uid_l1 = backData[:5]

    if uid_l1[0] == 0x88:
        sel_cmd = [0x93, 0x70] + uid_l1
        crc = reader.CalulateCRC(sel_cmd)
        sel_cmd += crc
        (status, _, _) = reader.MFRC522_ToCard(reader.PCD_TRANSCEIVE, sel_cmd)
        if status != reader.MI_OK:
            return None

        reader.Write_MFRC522(reader.BitFramingReg, 0x00)
        (status, backData, _) = reader.MFRC522_ToCard(
            reader.PCD_TRANSCEIVE, [0x95, 0x20]
        )
        if status != reader.MI_OK or len(backData) < 5:
            return None

        uid_l2 = backData[:5]
        sel_cmd = [0x95, 0x70] + uid_l2
        crc = reader.CalulateCRC(sel_cmd)
        sel_cmd += crc
        (status, _, _) = reader.MFRC522_ToCard(reader.PCD_TRANSCEIVE, sel_cmd)
        if status != reader.MI_OK:
            return None

        return uid_l1[1:4] + uid_l2[0:4]
    else:
        sel_cmd = [0x93, 0x70] + uid_l1
        crc = reader.CalulateCRC(sel_cmd)
        sel_cmd += crc
        reader.MFRC522_ToCard(reader.PCD_TRANSCEIVE, sel_cmd)
        return uid_l1[:4]

def read_tag():
    nfc_uri = []
    cur_page = 6
    eof = False

    while not eof:
        page_data = read_ntag_page(cur_page)
        if page_data is None:
            break

        start_i = 1 if cur_page == 6 else 0

        for i in range(start_i, READ_BUF_LEN - 2):
            byte = page_data[i]
            if byte == EOF_CHARACTER:
                eof = True
                break
            nfc_uri.append(chr(byte))

        cur_page += 4

    return ''.join(nfc_uri)

def write_ntag_page(page, data):
    if len(data) != 4:
        raise ValueError("Data must be exactly 4 bytes")
    
    cmd = [0xA2, page] + list(data)  # 0xA2 = NTAG WRITE command
    pOut = reader.CalulateCRC(cmd)
    cmd += pOut
    (status, backData, backLen) = reader.MFRC522_ToCard(reader.PCD_TRANSCEIVE, cmd)
    return status == reader.MI_OK

def write_tag(text):
    # Pad and encode the text
    data = [ord(c) for c in text] + [EOF_CHARACTER]
    
    # Pad to a multiple of 4 bytes (page size)
    while len(data) % 4 != 0:
        data.append(0x00)

    cur_page = 6
    first_page = True

    for i in range(0, len(data), 4):
        page_data = data[i:i+4]

        # First byte of page 6 is skipped on read, so pad with 0x00
        if first_page:
            page_data = [0x00] + page_data[:3]
            # remaining bytes spill to next chunk
            data = data[:i] + [0x00] + data[i:]  # shift data to account for padding
            first_page = False

        success = write_ntag_page(cur_page, page_data)
        if not success:
            print(f"Write failed at page {cur_page}")
            return False

        cur_page += 4

    return True

def rfid_read():
    while True:        
        reader.MFRC522_StopCrypto1()

        (status, TagType) = reader.MFRC522_Request(reader.PICC_REQIDL)
        if status != reader.MI_OK:
            continue

        uid = select_ntag()
        if uid is None:
            continue
        
        result = read_tag()
        if result:
            print("Read:", result)
        
        return

def rfid_write(write_str):
    while True:        
        reader.MFRC522_StopCrypto1()

        (status, TagType) = reader.MFRC522_Request(reader.PICC_REQIDL)
        if status != reader.MI_OK:
            continue

        uid = select_ntag()
        if uid is None:
            continue
        
        success = write_tag(write_str)
        print("Write success:", success)
        
        return
