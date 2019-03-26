import binascii
import sys
import struct

# Offset to apply to addresses when looking at a USB dump. This is because
# the first 4096-byte page of the SPI flash is not normally dumped via USB.
# We start at the second page, so addresses will be off by 1 page.
USB_ADDR_OFFSET = 0x1000

# Base of the address table.
PTR_BASE=0x2f010
OFFSET_NAME = 0x0
OFFSET_MSG1 = 0x38

class Rom(object):
  def __init__(self, contents):
    self.rom = contents
  def _get_table_addr(self, addr):
    return int.from_bytes(self.rom[addr:addr+4], byteorder='little')-USB_ADDR_OFFSET
  def _get_lfstring(self, rom, addr):
    return self.rom[addr:self.rom.find(b'\x00', addr)]
  def get_name_string(self):
    return self._get_lfstring(self.rom, self._get_table_addr(PTR_BASE+OFFSET_NAME)).decode("utf-8")
  def set_name_details(self, namestr, namesound):
    nameaddr = self._get_table_addr(PTR_BASE+OFFSET_NAME)
    pad = 0 if len(namestr)+1%4 == 0 else 4 - ((len(namestr)+1) % 4)
    payload = namestr + b'\x00' + (b'\xFF'*pad) + b'\x01\x00\xcf\x02' + namesound + b'\x11'
    self.rom = self.rom[:nameaddr] + payload + self.rom[nameaddr+len(payload):]
  def get_message1_string(self):
    return self._get_lfstring(self.rom, self._get_table_addr(PTR_BASE+OFFSET_MSG1)).decode("utf-8")


