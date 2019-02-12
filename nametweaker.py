from cmd import Cmd
import rom
import usb
import pdb

class NameTweakerPrompt(Cmd):
  def __init__(self):
    super(NameTweakerPrompt, self).__init__()
    self.rom = None
    self.usbclient = usb.client()

  def do_exit(self, inp):
    print("See ya!")
    return True

  def do_dump(self, inp):
    print("Dumping rom from Leaptop...")
    self.rom = rom.Rom(self.usbclient.dump())
    print("Success! To write rom to file use 'writefile'.")
  
  def do_writedevice(self, inp):
    print("Writing rom to Leaptop...")
    self.usbclient.upload(self.rom.rom)
    print("Success!")

  def do_writefile(self, inp):
    if not inp:
      print("Please specify a ROM filename to write!")
    with open(inp, 'wb') as f:
      f.write(self.rom.rom)
    print("Wrote current ROM to file {}".format(inp))

  def do_changename(self, inp):
    if not self.rom:
      print("No ROM loaded! You must either get ROM from the device or load it from a file.")
      return
    name, sound = inp.split(',')
    if len(name) > 8:
      print("Sorry, names >8 characters are not supported yet!")
      return
    print("Changing name to {}".format(name))
    with open(sound, 'rb') as f:
      soundcontents = f.read()
      self.rom.set_name_details(bytes(name.upper().encode('UTF-8')), soundcontents)

  def do_readfile(self, inp):
    if not inp:
      print("Please specify a ROM filename!")
      return
    with open(inp, 'rb') as f:
      self.rom = rom.Rom(f.read())
    print("Read rom from {}".format(inp))

  def do_rominfo(self, inp):
    print("Flash info:")
    print("Name: {}".format(self.rom.get_name_string()))


NameTweakerPrompt().cmdloop()
