# This script runs the canaries and controls their displays
import subprocess
import os
from screeninfo import get_monitors

# used to split the screen in two
monitor = get_monitors()[0]
width = monitor.width
half_width = int(monitor.width / 2)
height = int(monitor.height)

# This assumes this script and the canary scrips below are in the same directory
dir_path = os.path.dirname(os.path.realpath(__file__))
stream_2D = subprocess.Popen(['python3', f'{dir_path}/2D_image_stream.py',
                              '--payload', '<payload>',
                              '--address', '<address>',
                              '--resolution', f'{half_width}', f'{height}',
                              '--coordinates', '0', '0',
                              '--cam', 'cam'
                              ])

stream_other = subprocess.Popen(['python3', f'{dir_path}/2D_detection_stream.py',
                                 '--payload', '<payload>',
                                 '--address', '<address>',
                                 '--resolution', f'{half_width}', f'{height}',
                                 '--coordinates', f'{half_width}', '0',
                                 '--cam', 'cam2'
                                 ])

for p in [stream_2D, stream_other]:
    p.wait()
