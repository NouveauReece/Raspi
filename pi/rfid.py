from mfrc522 import MFRC522
import RPi.GPIO as GPIO
import time

READ_BUF_LEN = 18
EOF_CHARACTER = 254

def select_ntag():
    """Handle 7-byte UID cards requiring cascade level 2 anticollision"""

    # Level 1 anticollision
    reader.Write_MFRC522(reader.BitFramingReg, 0x00)
    (status, backData, _) = reader.MFRC522_ToCard(
        reader.PCD_TRANSCEIVE, [0x93, 0x20]
    )
    if status != reader.MI_OK or len(backData) < 5:
        print("Level 1 anticoll failed")
        return None

    uid_l1 = backData[:5]
    print("L1 raw:", [hex(x) for x in uid_l1])

    # If first byte is 0x88 (cascade tag), we need level 2
    if uid_l1[0] == 0x88:
        # Select with cascade tag to proceed to level 2
        sel_cmd = [0x93, 0x70] + uid_l1
        crc = reader.CalulateCRC(sel_cmd)
        sel_cmd += crc
        (status, _, backLen) = reader.MFRC522_ToCard(reader.PCD_TRANSCEIVE, sel_cmd)
        if status != reader.MI_OK:
            print("Level 1 select failed")
            return None

        # Level 2 anticollision
        reader.Write_MFRC522(reader.BitFramingReg, 0x00)
        (status, backData, _) = reader.MFRC522_ToCard(
            reader.PCD_TRANSCEIVE, [0x95, 0x20]
        )
        if status != reader.MI_OK or len(backData) < 5:
            print("Level 2 anticoll failed")
            return None

        uid_l2 = backData[:5]
        print("L2 raw:", [hex(x) for x in uid_l2])

        # Select level 2
        sel_cmd = [0x95, 0x70] + uid_l2
        crc = reader.CalulateCRC(sel_cmd)
        sel_cmd += crc
        (status, _, backLen) = reader.MFRC522_ToCard(reader.PCD_TRANSCEIVE, sel_cmd)
        if status != reader.MI_OK:
            print("Level 2 select failed")
            return None

        # Full 7-byte UID = bytes 1-3 of L1 + bytes 0-3 of L2
        full_uid = uid_l1[1:4] + uid_l2[0:4]
        print("Full 7-byte UID:", [hex(x) for x in full_uid])
        return full_uid

    else:
        # Normal 4-byte UID, just select normally
        sel_cmd = [0x93, 0x70] + uid_l1
        crc = reader.CalulateCRC(sel_cmd)
        sel_cmd += crc
        reader.MFRC522_ToCard(reader.PCD_TRANSCEIVE, sel_cmd)
        return uid_l1[:4]


def read_ntag_page(page):
    recvData = [0x30, page]
    pOut = reader.CalulateCRC(recvData)
    recvData += pOut
    (status, backData, backLen) = reader.MFRC522_ToCard(reader.PCD_TRANSCEIVE, recvData)
    if status == reader.MI_OK and len(backData) >= 4:
        return backData[:16]
    return None


def read_tag():
    nfc_uri = []
    cur_page = 6
    eof = False

    while not eof:
        page_data = read_ntag_page(cur_page)
        if page_data is None:
            print(f"Read failed at page {cur_page}")
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

def rfid_loop_call():
    reader.MFRC522_StopCrypto1()

    (status, TagType) = reader.MFRC522_Request(reader.PICC_REQIDL)
    if status != reader.MI_OK:
        return
    
    uid = select_ntag()
    if uid is None:
        print("UID None")
        return

    result = read_tag()
    print("Read:", result)


try:
    reader = MFRC522()
    
    while True:
        rfid_loop_call()
        time.sleep(1)

finally:
    GPIO.cleanup()
