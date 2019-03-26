#!/usr/bin/python3

import datetime
import sys
import converter
import rom
import usb

def main(argv):
  if len(argv) != 2:
    print("MyOwnLeaptop Name Changer...")
    print("Syntax: python3 namechanger.py <name> <audiofile>")
    return
  name = argv[0]
  audiofile = argv[1]
  print("Checking for necessary files...")
  converter.download_converter()
  print("Connecting to device. Make sure it's plugged in + turned on!")
  usbclient = usb.client()
  print("Backing up ROM...")
  myrom = rom.Rom(usbclient.dump())
  bakfile = "backup-{}.rom".format(str(datetime.datetime.now()))
  with open(bakfile, 'wb') as f:
    f.write(myrom.rom)
    print("Wrote current ROM to file {}".format(bakfile))
  print("Converting audio file...")
  converter.convert_audiofile(audiofile)
  if len(name) > 8:
    print("Sorry, names >8 characters are not supported yet!")
    return
  print("Changing name to {}".format(name))
  with open('tmp.wav.adp', 'rb') as f:
    soundcontents = f.read()
    myrom.set_name_details(bytes(name.upper().encode('UTF-8')), soundcontents)
  print("Writing rom to Leaptop...")
  usbclient.upload(myrom.rom)
  print("Success!")

if __name__ == "__main__":
   main(sys.argv[1:])
