# myleaptop utility, modified from OpenLFConnect pager.py
import binascii
import os
import sys
import time
import struct
from shlex import split as shlex_split
from subprocess import Popen, PIPE

PACKET_SIZE = 4096
FLASH_LEN = 520192

def swap32(i):
    return struct.unpack("<I", struct.pack(">I", i))[0]

def gpchecksum(buf):
  mysum = 0
  for c in buf:
    mysum += c
  return swap32(mysum)

class client(object):
    def __init__(self, device_id=None, debug=False):
        self.debug = debug
        self._timeout = 10
        self._vendor_name = 'leapfrog'
        self._sg_raw = '/bin/sg_raw' if sys.platform == 'win32' else 'sg_raw'
        self._sg_scan = '/bin/sg_scan' if sys.platform == 'win32' else 'sg_scan'
        self._device_id = device_id if device_id else self.find_device_id()

    def error(self, e):
        assert False, 'Error: %s' % e

    def write_cmd(self, op, seq=None, data=None):
      
      cmdl = '%s %s %s %s' % (self._sg_raw, self._device_id, opts, cmd_block)
      cmd = shlex_split

    def dump(self):
        try:                    
            buf = b''
            
            packets = int(FLASH_LEN/PACKET_SIZE)
            total = 0
            last_total = 0
            for i in range(0, packets):
                bts = '{0:04x}'.format(((i + 1) * 0x10))
                byte1 = bts[0:2]
                byte2 = bts[2:4]
                cmdl = '%s %s -b -r %s -n FD 28 00 %s %s 00 06 00 08 00 00 00 00 00 47 50' % (self._sg_raw, self._device_id, PACKET_SIZE, byte1, byte2)
                cmd = shlex_split(cmdl)
                if self.debug:
                  print("Write Cmd = %s" % cmdl)
                p = Popen(cmd, stdout=PIPE, stderr=PIPE)
                err = p.stderr.read()
                data = p.stdout.read()
                
                if not b'Good' in err:
                    self.error('SCSI error: {}'.format(err))
                else:
                    buf += data
            end = bytearray()
            end.extend(buf[0:0x2eff0])
            end.extend(b'\xFF' * 20)
            end.extend(buf[0x2f004:-4])
            end.extend(b'\xFF' * 4)
            return end

        except Exception as e:
            self.error(e)
            return None

    def blank_page(self, num_pages, start):
        for i in range(start, num_pages+start):
            bts = '{0:04x}'.format(((i + 1) * 0x10))
            byte1 = bts[0:2]
            byte2 = bts[2:4]
            cmdl = '%s %s -n FD 20 00 %s %s 00 06 00 08 00 00 00 00 00 47 50' % (self._sg_raw, self._device_id, byte1, byte2)
            cmd = shlex_split(cmdl)
            if self.debug:
              print("Blanking Cmd = %s" % cmdl)
            p = Popen(cmd, stderr=PIPE)
            err = p.stderr.read()

            if not b'Good' in err:
               self.error('SCSI error: %s' % err)
    def start_checksum(self):
        cmdl = '%s %s -n E0 B1 00 00 00 00 00 00 00 00 00 00 00 00 47 50' % (self._sg_raw, self._device_id)
        cmd = shlex_split(cmdl)
        print("Device is calculating checksum. This should take ~30sec.")
        if self.debug:
          print("Checksum cmd = %s" % cmdl)
        p = Popen(cmd, stderr=PIPE)
        _, err = p.communicate(self._timeout)
        if not b'Good' in err:
            self.error('SCSI error.' % err) 

    def wait_finish(self):
      print("Waiting for checksum finish...")
      finished = False
      while not finished:
        cmdl = '%s %s -r 2 -b D0 BC 00 00 00 00 00 00 00 00 00 00 00 00 47 50' % (self._sg_raw, self._device_id)
        cmd = shlex_split(cmdl)
        p = Popen(cmd, stderr=PIPE, stdout=PIPE)
        err = p.stderr.read()
        if not b'Good' in err:
          self.error('SCSI error: %s' % err)
        out = p.stdout.read()
        if out == b'\xbd\x00':
          finished = True
        elif out == b'\xbd\x01':
          self.error('Checksum error from device!')
        else:
          print("Still waiting for checksum to complete...")
          time.sleep(self._timeout)

    def upload(self, rom):
        try:
            print("Waiting for the device to settle... (20 sec)")
            time.sleep(20)
            buf = bytearray()
            
            ck1 = '{0:08x}'.format(gpchecksum(rom[4:(0x2f000-4)]))
            print('Checksum 1: {0}'.format(ck1))
            ck2 = '{0:08x}'.format(gpchecksum(rom[0x2f004:-4]))
            print('Checksum 2: {0}'.format(ck2))
            
            buf.extend(binascii.a2b_hex(ck1))
            buf.extend(rom[4:0x2f000])
            buf.extend(binascii.a2b_hex(ck2))
            buf.extend(rom[0x2f004:])
            buf_len = len(buf)
            if buf_len != 520192:
              self.error('File is wrong size for MyLeaptop, must be 520192 bytes!')

            packets = int(buf_len/PACKET_SIZE)
            total = 0
            last_total = 0
            print("Writing ROM to the device...")
            self.blank_page(0x2f, 0)
            for i in range(0, packets):
                if i == 0x2f:
                  self.blank_page(0x50, i)
                bts = '{0:04x}'.format(((i + 1) * 0x10))
                fs = 'f' * PACKET_SIZE
                cur = buf[last_total:last_total+PACKET_SIZE]
                byte1 = bts[0:2]
                byte2 = bts[2:4]
                cmdl = '%s %s -b -s %s -n FD 2A 00 %s %s 00 06 00 08 00 00 00 00 00 47 50' % (self._sg_raw, self._device_id, PACKET_SIZE, byte1, byte2)
                cmd = shlex_split(cmdl)
                if self.debug:
                  print("Cmd = %s" % cmdl)
                p = Popen(cmd, stdin=PIPE, stderr=PIPE)
                _, err = p.communicate(cur, self._timeout)
                
                if not b'Good' in err:
                    self.error('SCSI error: %s' % err)
                last_total += PACKET_SIZE

            self.start_checksum()
            self.wait_finish()
        except Exception as e:
            self.error(e)

    def find_device_id(self):
        try:
            timeout = self._timeout

            while timeout:
                if sys.platform == 'win32':
                    lines = self.sg_scan().split('\n')
                    if lines:
                        for line in lines:
                            if self._vendor_name in line.lower():
                                if sys.platform == 'win32':
                                    _device_id = '%s' % line.split(' ')[0]
                                else:
                                    _device_id = '%s' % lines[lines.index(line) -1].split(' ')[0].replace(':', '')
                
                                return _device_id

                else:
                    vendor_pattern = '/sys/class/scsi_disk/%s:0:0:0/device/vendor'
                    blockdev_pattern = '/sys/class/scsi_disk/%s:0:0:0/device/block'

                    for i in range(0, 100):
                        vendor_path = vendor_pattern % (i)

                        if os.path.exists(vendor_path):
                            f = open(vendor_path, 'r')
                            vendor = f.readline()
                            f.close()

                            if vendor.rstrip().lower() == self._vendor_name:
                                for sdx in os.listdir(blockdev_pattern % i):
                                    if sdx.startswith('sd'):
                                        _device_id = '/dev/%s' % sdx
                                        return _device_id
                                                        
                timeout -= 1
                time.sleep(1)
            self.error('Device not found.')
        except Exception as e:
            self.error(e)
