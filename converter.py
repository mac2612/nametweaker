#!/usr/bin/python3

import os
import pydub
from pydub import AudioSegment
import subprocess
from pathlib import Path
import urllib.request

def download_converter():
  if Path("AudioBatchConverter.exe").exists() and Path("ADPCM66.dll").exists() and Path('AlgorithmAgent.dll').exists():
    print("Already downloaded AudioFormatConverter. Skipping download...")
    return
  dll1_url = 'https://github.com/LiteracyBridge/acm/raw/master/acm/converters/a18/ADPCM66.dll'
  dll2_url = 'https://github.com/LiteracyBridge/acm/raw/master/acm/converters/a18/AlgorithmAgent.dll'
  exe_url = 'https://github.com/LiteracyBridge/acm/raw/master/acm/converters/a18/AudioBatchConverter.exe'
  print("Downloading ADPCM66.dll from github...")
  urllib.request.urlretrieve(dll1_url, 'ADPCM66.dll')
  urllib.request.urlretrieve(dll2_url, 'AlgorithmAgent.dll')
  print("Downloading AudioBatchConverter.exe from github...")
  urllib.request.urlretrieve(exe_url, 'AudioBatchConverter.exe')

def convert_to_adpcm(wav_file, bitrate, algo='ADPCM66'):
  cmd = "AudioBatchConverter.exe -e {} -b {} -h No -o . {}".format(algo, bitrate, wav_file)
  # On non-windows system, use wine. You'll need to install wine for this.
  if os != 'nt':
    cmd = "wine " + cmd
  print("cmd = " + cmd)
  conv = subprocess.Popen(cmd, shell=True)
  conv.wait()
  return wav_file + '.adp'

def convert_audiofile(input_file, bitrate=9000):
  sound = AudioSegment.from_file(input_file)
  sound = sound.set_frame_rate(bitrate)
  sound.export('tmp.wav', format="wav")
  return convert_to_adpcm('tmp.wav', bitrate=bitrate)

#download_converter()
#convert_to_adpcm("newman2.wav")
#convert_audiofile("test.mp3")
