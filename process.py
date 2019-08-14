import sys
import re
from utils import *

if os.name != 'nt':
	print('As of now, only Windows is supported. :(')
	exit()

if len(sys.argv) < 3:
	print('Usage: process.py <ssc file path> <result file path>')
	exit()

ssc_filepath = sys.argv[1]
result_filepath = sys.argv[2]

print(f'Searching for all routine charts in "{ssc_filepath}".')

routines = find_routines(ssc_filepath)
print(f'The routine charts in "{scc_filepath}" are {routines}.')

copy_file(ssc_filepath, result_filepath)

result_file = open(result_filepath, 'a')

for (description, chart_type) in routines:
	# Splitting more than two players chart is not implemented yet.
	if chart_type == 'stepf2more':
		continue
	
	ssc_file = open(ssc_filepath, 'r')
	split_routine(ssc_file, description, result_file, chart_type)
	ssc_file.close()

result_file.close()