from datetime import datetime
import subprocess
from time import sleep
import os
from pywinauto.findwindows import find_window
from logging import info
from colorama import Fore, Style
from time import sleep
# just_fix_windows_console()
YELLOW = Fore.YELLOW
MAGENTA = Fore.LIGHTMAGENTA_EX
RESET = Style.RESET_ALL







scrcpy_path = os.path.expanduser("~") + '\\PortableApps\\scrcpy-win64-v2.6.1\\scrcpy.exe'
output_path = 'E:\\'
buffer = 150    # buffer value in ms
bitrate = 4 # MBPS




devices = { #mode: screencap | cameracap | audiomirror

  # 'RA2Plus': { 
  #   'serial': "GIE655CM9L6X5P7D", 
  #   'mode': "screencap", 
  #   'px-width': 1920,  # if screencap, this will applied to window-height
  #   'fps': 30, 
  #   'audio_playback': 'muted',
  #   'mic_capture': False,
  #   'codec': 'h264'
  # },
  # 'OppoA79': {
  #   'serial': "GQCEPFAQGEMZG6N7", 
  #   'mode': "screencap", 
  #   'px-width': 1080, #A14 does not support --crop
  #   'fps': 30, 
  #   'audio_playback': 'play',
  #   'mic_capture': False,
  #   'codec': 'h265'
  # },
  'RN10Pro': {
    'serial': "b34c3001", 
    'mode': "cameracap",
    'px-width': 1280,  # refereace to landscape measurements, max=2720x1530
    'orientation': 'portrait', # 'portrait' | 'landscape'
    'fps': 30, 
    'audio_loudspeaker': False,   # True | False
    'mic_capture': False,
    'codec': 'h265' # 'h265' | 'h264'
  },
}





# initialize device names only from dict
device_names = list(devices.keys())

### SETTINGS FOR ALL DEVICES
for name in device_names:
  devices[name]['ipaddr'] = None # init do not touch
  devices[name]['bool_conn'] = False # init do not touch
  devices[name]['savetofile'] = True # TRUE | FALSE
  devices[name]['enable_control'] = False # TRUE | FALSE




try:
  while True:
    for name in device_names:
      serial = devices[name]['serial']
      mode = devices[name]['mode']
      width:int = devices[name]['px-width']
      orientation:str = devices[name]['orientation']
      fps = str(devices[name]['fps'])
      audioplayback = devices[name]['audio_loudspeaker'] # return bool
      miccap = devices[name]['mic_capture'] # return bool
      codec = devices[name]['codec'] # return "h264" | "h265"
      ip_address = devices[name]['ipaddr']
      boolconn = devices[name]['bool_conn']
      enablesave = devices[name]['savetofile'] # return bool
      enablecontrol = devices[name]['enable_control'] # return bool
      
      try:
        find_window(title=name)
        info(f"Window {name} of ip {ip_address} is active.")
      
      except Exception:
        
        print(f'No window {name} is active. Starting/ restarting scrcpy for {name}.')
        
        if boolconn == False:
          result = subprocess.run(['adb', '-s', serial, 'shell', 'ip', '-f', 'inet', 'addr', 'show', 'wlan0'], capture_output=True, text=True)
          output_lines = result.stdout.split('\n')
          for line in output_lines:
            if ('inet' in line) and ('wlan0' in line):
              ip_address = line.split()[1].split('/')[0]
              devices[name]['ipaddr'] = ip_address
              devices[name]['bool_conn'] = True

          subprocess.run(['adb', '-s', serial, 'tcpip', '5555'], capture_output=True, text=True)

        while True:  
          try:
            subprocess.run(['adb', 'connect', ip_address], capture_output=True, text=True)
            break
          except TypeError:
            print(YELLOW+'NOTICE: Waiting for user to connect device physically using a wire...'+RESET, end="\r")
            sleep(0.1)
          
        dat = datetime.now().strftime('%y%m%d%H%M%S')



        scrcpyInit = f'{scrcpy_path} --tcpip={ip_address}:5555 --print-fps --window-borderless -b {bitrate}M' 
        # target scrcpy to device serial, wirelessly, borderless window, 8mbps

        # image orientation logic
        if orientation == 'portrait':    scrcpyInit += f' --window-height={width} --orientation=90'
        elif orientation == 'landscape': scrcpyInit += f' --window-width={width} --orientation=270'
        
        # no logic for window title, display buffer, audio buffer, video codec
        scrcpyInit += f' --window-title={name} --display-buffer={buffer} --audio-buffer={buffer} --video-codec={codec}'  # 

        ### IF...ELSE MODE
        if (mode == 'screencap'):   scrcpyInit += f' --max-fps={fps}'
        elif (mode == 'cameracap') or (mode == 'highspeed'): 
          if mode == 'highspeed':  scrcpyInit += f' --camera-high-speed'
          scrcpyInit += f' --camera-fps={fps} --video-source=camera --camera-id=0 --camera-size={width}x{int((width/16)*9)}'

        # logic for enable control, mic capture, audio playback, enable save
        if (enablecontrol == False): scrcpyInit += ' --no-control'
        if (miccap == True):         scrcpyInit += f' --audio-source=mic'
        if (audioplayback == False): scrcpyInit += f' --no-audio-playback'
        if (enablesave == True):     scrcpyInit += f' -r "{output_path}{name}_{dat}.mkv"' # "~/videos/devicename/..."

        print(MAGENTA,scrcpyInit,RESET)            # print resulting scrcpy command
        subprocess.Popen(scrcpyInit) # run the scrcpy command

      sleep(3)


except (KeyboardInterrupt or Exception):
    
  print('ERROR: KeyboardInterrupt received. Killing any scrcpy processes and killing adb...')
  subprocess.run(['adb', 'kill-server'])