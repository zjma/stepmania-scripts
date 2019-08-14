import os
import re
import subprocess
import shutil
import sys
from utils import *

if len(sys.argv) < 2:
	print('Usage: walk.py <root_directory> <target_root_directory>')
	exit()

root_dir = sys.argv[1]
target_root_dir = sys.argv[2]

print('Splitting all routine charts inside "{}".'.format(root_dir))

# Walk on all subdirectories and find the ones that have sscs.
for sub_dir, dirs, files in os.walk(root_dir):
	for filename in files:
		# If the directory contains an ssc, check if it has a rountine chart.
		if filename.endswith('.ssc'):
			filepath = sub_dir + os.sep + filename
			print('Processing {0}'.format(filepath))
			# Find and split all the routine charts.
			subprocess.call(['python', 'process.py', filepath, 'tmp'])
			# Copy all the contents from the source directory to the target.
			target_sub_dir = sub_dir.replace(root_dir, target_root_dir, 1)
			shutil.copytree(sub_dir, target_sub_dir)
			# Move the new chart to the target directory.
			shutil.move('tmp', target_sub_dir + os.sep + filename)
