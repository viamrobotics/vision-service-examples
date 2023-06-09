import os
import subprocess

import json

HOME = os.path.expanduser('~')
canary_secrets = f'{HOME}/.canary_secrets.json'
f = open(canary_secrets)
data = json.load(f)
f.close()
secret = data['canary']['secret']
address = data['canary']['address']

# This assumes this script and the script below are in the same directory
dir_path = os.path.dirname(os.path.realpath(__file__))
stream = subprocess.Popen(['python3', f'{dir_path}/stream.py',
                              '--secret', secret,
                              '--address', address
                          ])
stream.wait()
