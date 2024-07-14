from datetime import datetime
import subprocess
from time import sleep
import os
import re
from pywinauto import Application
from pywinauto.findwindows import find_window, WindowNotFoundError
from logging import info
import argparse








scrcpy_path = os.path.expanduser("~") + '\\PortableApps\\scrcpy-win64-v2.4\\scrcpy.exe'
output_path = 'E:\\'
buffer = 70    # buffer value in ms


devices = {
  # 'RedmiN7': { 
  #   'serial': "b309ccb2", 
  #   'mode': "screencap", 
  #   'dimensions': None, 
  #   'fps': 30, 
  #   'audio_playback': 'play',
  #   'mic_capture': True,
  # },
  # 'OppoA79': {
  #   'serial': "GQCEPFAQGEMZG6N7", 
  #   'mode': "screencap", 
  #   'dimensions': None, #A14 does not support --crop
  #   'fps': 30, 
  #   'audio_playback': 'muted',
  #   'mic_capture': True,
  # },
  'RN10Pro': {
    'serial': "b34c3001", 
    'mode': "screencap", 
    'dimensions': None,
    'fps': 30, 
    'audio_playback': 'play',
    'mic_capture': False,
  },
}



device_names = list(devices.keys())



### SETTINGS FOR ALL DEVICES
for name in device_names:
  devices[name]['ipaddr'] = None
  devices[name]['bool_conn'] = False
  devices[name]['savetofile'] = False
  devices[name]['enable_control'] = True




try:

  while True:

    for name in device_names:
      
      serial = devices[name]['serial']
      mode = devices[name]['mode']
      dimensions = devices[name]['dimensions']
      fps = str(devices[name]['fps'])
      
      ip_address = devices[name]['ipaddr']
      boolconn = devices[name]['bool_conn']
      audioplayback = devices[name]['audio_playback']
      miccap = devices[name]['mic_capture'] # return bool
      enablesave = devices[name]['savetofile'] # return bool
      enablecontrol = devices[name]['enable_control'] # return bool
      


      try:
      
        find_window(title=name)
        info(f"Window {name} of ip {ip_address} is active.")
      
      except Exception:
        
        print(f'No window {name} is active. Starting/ restarting scrcpy for {name}.')
        
        if boolconn == False:
          result = subprocess.run(['adb', '-s', serial, 'shell', 'ip', '-f', 'inet', 'addr', 'show', 'wlan0'], capture_output=True, text=True)
          info(result)
          output_lines = result.stdout.split('\n')
          for line in output_lines:
            if 'inet' in line and 'wlan0' in line:
              ip_address = line.split()[1].split('/')[0]
              info(ip_address)
              devices[name]['ipaddr'] = ip_address
              devices[name]['bool_conn'] = True

          subprocess.run(['adb', '-s', serial, 'tcpip', '5555'])
          try:
            subprocess.run(['adb', 'connect', ip_address])
          except TypeError:
            print('ERROR: Have you connect your device physically using a wire?')
            exit(1)
          
        dat = datetime.now().strftime('%y%m%d%H%M%S')

        scrcpyInit = f'{scrcpy_path} --tcpip={ip_address}:5555 --window-borderless -b 6M' 
        # target scrcpy to device serial, wirelessly, borderless window, 8mbps

        scrcpyInit += f' --window-height=1080 --window-title={name} --display-buffer={buffer}'
        # set window height 1080px, window title name, no audio, 300ms display buffer



        ### IF ENABLE CONTROL IS TRUE
        if (enablecontrol == False):
          scrcpyInit += ' --no-control'
        
        

        ### IF...ELSE SCREEN CAPTURE MODE

        if (mode == 'screencap'):
          scrcpyInit += f' --max-fps={fps} --lock-video-orientation=270'
          # set max fps, lock video orientation to landscape
          if dimensions != None:
            scrcpyInit += f' --crop={dimensions}'
        elif (mode == 'cameracap'):
          scrcpyInit += f' --camera-fps={fps} --video-source=camera --camera-id=0 --camera-size={dimensions}'
          # set max fps, video source camera, front camera, camera size=dimensions


        ### IF MIC CAPTURE SET TO TRUE
        if (miccap == True):
          scrcpyInit += f' --audio-source=mic'


        scrcpyInit += f' --audio-buffer={buffer} --video-codec=h265 --audio-codec=aac'
        
        if (audioplayback == 'muted'):
          scrcpyInit += f' --no-audio-playback'
        
        if (enablesave == True):
          scrcpyInit += f' -r "{output_path}{name}_{dat}.mkv"'
        # -record to filename= ~/videos/devicename/...

        print(scrcpyInit)

        subprocess.Popen(scrcpyInit)

      sleep(3)



except (KeyboardInterrupt or Exception):
    
  print('ERROR: KeyboardInterrupt received. Killing any scrcpy processes and killing adb...')
  subprocess.run(['adb', 'kill-server'])