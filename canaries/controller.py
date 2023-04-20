# This script runs the canaries and controls their displays
import subprocess
import os
from screeninfo import get_monitors
import json

# used to split the screen in two
monitor = get_monitors()[0]
width = monitor.width
half_width = int(monitor.width / 2)
height = int(monitor.height)

HOME = os.path.expanduser('~')
canary_secrets = f'{HOME}/.canary_secrets.json'
f = open(canary_secrets)
data = json.load(f)
payload = data['canary']['payload']
address = data['canary']['address']
f.close()


# This assumes this script and the canary scrips below are in the same directory
dir_path = os.path.dirname(os.path.realpath(__file__))
stream_2D = subprocess.Popen(['python3', f'{dir_path}/2D_image_stream.py',
                              '--payload', payload,
                              '--address', address,
                              '--resolution', f'{half_width}', f'{height}',
                              '--coordinates', '0', '0',
                              '--cam', 'standard_camera'
                              ])

stream_other = subprocess.Popen(['python3', f'{dir_path}/2D_detection_stream.py',
                                 '--payload', payload,
                                 '--address', address,
                                 '--resolution', f'{half_width}', f'{height}',
                                 '--coordinates', f'{half_width}', '0',
                                 '--cam', 'transform_camera'
                                 ])

for p in [stream_2D, stream_other]:
    p.wait()
