from datetime import datetime
import subprocess
from time import sleep
import os
from pywinauto.findwindows import find_window
from logging import info








scrcpy_path = os.path.expanduser("~") + '\\PortableApps\\scrcpy-win64-v2.6.1\\scrcpy.exe'
output_path = 'E:\\'
buffer = 150    # buffer value in ms
# encoderstring = 'OMX.google.h264.encoder'
bitrate = 16 # MBPS




devices = { #mode: screencap | cameracap | audiomirror

  'RA2Plus': { 
    'serial': "GIE655CM9L6X5P7D", 
    'mode': "screencap", 
    'px-width': 1920,  # if screencap, this will applied to window-height
    'fps': 30, 
    'audio_playback': 'muted',
    'mic_capture': False,
    'codec': 'h264'
  },
  # 'OppoA79': {
  #   'serial': "GQCEPFAQGEMZG6N7", 
  #   'mode': "highspeed", 
  #   'dimensions': '1280x720', #A14 does not support --crop
  #   'fps': 120, 
  #   'audio_playback': 'muted',
  #   'mic_capture': False,
  # },
  # 'RN10Pro': {
  #   'serial': "b34c3001", 
  #   'mode': "cameracap",
  #   'dimensions': '2720x1530',  # 2720x1530 is max resolution scrcpy can capture
  #   'fps': 30, 
  #   'audio_playback': 'muted',   # play | muted
  #   'mic_capture': False,
  # },
}



device_names = list(devices.keys())



### SETTINGS FOR ALL DEVICES
for name in device_names:
  devices[name]['ipaddr'] = None # init do not touch
  devices[name]['bool_conn'] = False # init do not touch
  devices[name]['savetofile'] = False # TRUE | FALSE
  devices[name]['enable_control'] = False # TRUE | FALSE




try:
  
  windowcheck = True

  while True:

    for name in device_names:
      
      serial = devices[name]['serial']
      mode = devices[name]['mode']
      width: int = devices[name]['px-width']
      fps = str(devices[name]['fps'])
      audioplayback = devices[name]['audio_playback']
      miccap = devices[name]['mic_capture'] # return bool
      codec = devices[name]['codec'] # return str = h264 | h265
      
      ip_address = devices[name]['ipaddr']
      boolconn = devices[name]['bool_conn']
      enablesave = devices[name]['savetofile'] # return bool
      enablecontrol = devices[name]['enable_control'] # return bool
      
      try:
        
        if windowcheck == True:
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

        scrcpyInit = f'{scrcpy_path} --tcpip={ip_address}:5555 --print-fps --window-borderless -b {bitrate}M' 
        # target scrcpy to device serial, wirelessly, borderless window, 8mbps

        scrcpyInit += f' --window-height={int((width/16)*9)} --window-title={name} --display-buffer={buffer}'
        # set window height 1080px, window title name, no audio, 300ms display buffer



        ### IF ENABLE CONTROL IS TRUE
        if (enablecontrol == False):
          scrcpyInit += ' --no-control'
        
        

        ### IF...ELSE MODE

        if (mode == 'screencap'):
          scrcpyInit += f' --max-fps={fps} --lock-video-orientation=270'
          # set max fps, lock video orientation to landscape
          # if width != None:
          #   scrcpyInit += f' --crop={width}'
        elif (mode == 'cameracap'):
          scrcpyInit += f' --camera-fps={fps} --video-source=camera --camera-id=0 --camera-size={width}x{int((width/16)*9)}'
          # set max fps, video source camera, front camera, camera size=width
        elif (mode == 'highspeed'):
          scrcpyInit += f' --camera-fps={fps} --camera-high-speed --video-source=camera --camera-id=0 --camera-size={width}'
        elif (mode == 'audiomirror'):
          scrcpyInit += f' --no-video-playback'
          windowcheck = False



        ### IF MIC CAPTURE SET TO TRUE
        if (miccap == True):
          scrcpyInit += f' --audio-source=mic'


        scrcpyInit += f' --audio-buffer={buffer} --video-codec={codec} --audio-codec=aac'
        # scrcpyInit += f' --audio-buffer={buffer} --video-codec={codec} --video-encoder="{encoderstring}" --audio-codec=aac'
        
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