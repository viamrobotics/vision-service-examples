import argparse
import os
import subprocess

parser = argparse.ArgumentParser()
parser.add_argument('--config_name', type=str, required=True, help='the config name')
args = parser.parse_args()

# This assumes this script and the script below are in the same directory
dir_path = os.path.dirname(os.path.realpath(__file__))
stream = subprocess.Popen(['python3', f'{dir_path}/stream.py',
                              '--config_name', args.config_name])
stream.wait()
