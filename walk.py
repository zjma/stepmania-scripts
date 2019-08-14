import os
import re
import shutil
import sys
from utils import *

if os.name != 'nt':
	print('As of now, only Windows is supported. :(')
	exit()

if len(sys.argv) < 3:
	print('Usage: walk.py <root_directory> <target_root_directory>')
	exit()

script_path = os.path.dirname(sys.argv[0])
root_dir = sys.argv[1]
target_root_dir = sys.argv[2]

print(f'Splitting all routine charts inside "{root_dir}".')

# Walk on all subdirectories and find the ones that have sscs.
for sub_dir, dirs, files in os.walk(root_dir):
	for filename in files:
		# If the directory contains an ssc, check if it has a rountine chart.
		if filename.endswith('.ssc'):
			filepath = os.path.join(sub_dir, filename)
			print(f'Processing {filepath}')
			# Find and split all the routine charts.
			subprocess.call(['python', os.path.join(script_path, 'process.py'),
					filepath, 'tmp'])
			# Copy all the contents from the source directory to the target.
			target_sub_dir = sub_dir.replace(root_dir, target_root_dir, 1)
			shutil.copytree(sub_dir, target_sub_dir)
			# Move the new chart to the target directory.
			shutil.move('tmp', os.path.join(target_sub_dir, filename))
