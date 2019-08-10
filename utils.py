import sys
import re

def gcd(a,b):
    """Compute the greatest common divisor of a and b"""
    while b > 0:
        a, b = b, a % b
    return a
    
def lcm(a, b):
    """Compute the lowest common multiple of a and b"""
    return a * b / gcd(a, b)

def copy_file(source_filepath, target_filepath):
	with open(source_filepath, 'r') as s:
	    with open(target_filepath, 'w') as t:
	        for line in s:
	            t.write(line)

def readLineUntilValid(file, line_count_offset=0, is_comment_invalid=True):
	line = '\n'
	line_count = line_count_offset
	while line == '\n' or (is_comment_invalid and line[:2] == '//'):
		line = file.readline()
		line = line if line == '\n' else line.lstrip()
		line_count += 1

	return line, line_count

def addSub(s, t, sub):
	"""Substitute add t's steps in s as sub."""
	# Initialize result.
	r = []

	# Initialize iterators.
	s_i = 0
	t_i = 0

	# List that stores whether there is a current hold for s.
	s_hold = [False for _ in range(10)]

	# Main loop for the whole chart.
	while True:
		# Read one block (until ',') in s.
		s_block = []
		s_line = s[s_i][:-1]
		s_i += 1
		while s_line[0] != ',' and s_line[0] != ';':
			s_block.append(s_line)
			s_line = s[s_i][:-1]
			s_i += 1

		# Read one block (until ',') in t.
		t_block = []
		t_line = t[t_i][:-1]
		t_i += 1
		while t_line[0] != ',' and t_line[0] != ';':
			t_block.append(t_line)
			t_line = t[t_i][:-1]
			t_i += 1

		# Calculate the number of lines in the resulting block.
		# The number of lines is the lowest common multiple of the lengths of
		# the two blocks.
		r_line_cnt = int(lcm(len(s_block),len(t_block)))

		# Calculate the period to determine in which iterations each block
		# should be processed. s will be processed in multiples of
		# s_period and t will be processed in multiples of t_period.
		s_period = r_line_cnt / len(s_block)
		t_period = r_line_cnt / len(t_block)

		# Iterate over a block.
		for i in range(r_line_cnt):
			# Initialize the resulting line with all 0.
			r_line = ['0' for _ in range(10)]

			# Process s if the iteration is multiple of s_period or there
			# are any pending holds.
			if i % s_period == 0:
				s_line = s_block[int(i/s_period)]
				for j, c in enumerate(s_line):
					if c != '0' or s_hold[j]:
						# Put a mine if there is an arrow or a hold.
						r_line[j] = sub
					if c == '2':
						# Set hold position j as true.
						s_hold[j] = True
					elif c == '3':
						# Reset hold in position j.
						s_hold[j] = False
			elif any(s_hold):
				# Process s' holds even if the iteration is not a multiple
				# of s_period.
				for j in range(10):
					if s_hold[j]:
						# Put a mine if there is a hold.
						r_line[j] = sub

			# Process t if the iteration is multiple of t_period.
			# Holds don't need to be processed separately.
			if i % t_period == 0:
				t_line = t_block[int(i/t_period)]
				for j, c in enumerate(t_line):
					if c != '0':
						# Put the original step.
						r_line[j] = c

			# Add line to the result.
			r.append(''.join(r_line) + '\n')

		# Check if this is the end of the chart or of the block.
		if s_i >= len(s)-1 or t_i >= len(t)-1:
			# Check if both s and t ended.
			if s_i >= len(s)-1 and t_i >= len(t)-1:
				# Add the chart-ending character.
				r.append(';\n')
				break
			else:
				print('One of them finished and the other not :(')
		else:
			# Add a block-ending character.
			r.append(',\n')
	return r

def substitute(s, sub):
	"""Substitute [1-9] digits for sub."""
	# Initialize result.
	r = []
	for line in s:
		if line.startswith(','):
			r.append(line)
		else:
			r.append(re.sub(r'[1-9]', 'F', line))

	return r

def mirror(s):
	"""Mirror all the lines."""
	# Initialize result.
	r = []

	# Mirror each line of the chart.
	for line in s:
		if line.startswith(','):
			r.append(line)
		else:
			r.append(line[9::-1]+'\n')

	return r

def read_header(ssc, line_number):
	"""Read the ssc until the end of the header.
	Returns: header, description and steps type."""
	# Initialize header with empty string that will be filled in the end of
	# the method.
	header = ['']

	# Get first line.
	line, line_number = readLineUntilValid(ssc, line_number)

	while True:
		if line.startswith('#STEPSTYPE'):
			steps_type = line.split(':')[1].split(';')[0]
			line = '#STEPSTYPE:{steps_type};\n'
		elif line.startswith('#DESCRIPTION'):
			# The description should match with the description in the
			# parameters.
			description = line.split(':')[1].split(';')[0]
			print('Processing "{}"\n'.format(description))
			line = '#DESCRIPTION:' + description + '[{variation}];\n'
		elif line.startswith('#DIFFICULTY'):
			# Difficulty should always be "Edit".
			line = '#DIFFICULTY:Edit;\n'

		header.append(line)
		line, line_number = readLineUntilValid(ssc, line_number)

		if line.startswith('#NOTES'):
			header.append(line)
			break

	# Set first line of the header with the correct description.
	header[0] = '//------------{steps_type} ' + description + '------------\n'

	return header, description, steps_type

def read_and_split_routine_stepmania(ssc, line_number):
	"""Read until the end of the notes of a stepmania routine chart.
	Returns: left and right charts separated."""
	# Get first line.
	line, line_number = readLineUntilValid(ssc, line_number)

	print('Left is starting in line {}: "{}".'.format(line_number, line))
	left = []
	while line[0] != '&':
		left.append(line)
		line, line_number = readLineUntilValid(ssc, line_number)
	left.append(';\n')

	# Skip '&'.
	while line[0] == '&' or line == '\n':
		line, line_number = readLineUntilValid(ssc, line_number)

	print('Right is starting in line {}.'.format(line_number))
	right = []
	while line[0] != ';':
		right.append(line)
		line, line_number = readLineUntilValid(ssc, line_number)
	right.append(';\n')

	return left, right

def split_routine_stepf2_line(line, my_char, other_char, my_hold):
	"""Extract one player's line from a stepf2 routine line.
	Returns: one player's line."""
	tmp_line = (line.replace(other_char.upper(), '0') # Remove other's taps.
			.replace(other_char.lower(), '0') # Remove other's hold starts.
			.replace(my_char.upper(), '1') # Add my taps.
			.replace(my_char.lower(), '2')) # Add my hold starts.
		
	# Remove other's hold ends.
	return ''.join([tmp_line[i] if tmp_line[i] != '3' or my_hold[i] else '0' for i in range(10)]) + '\n'

def update_hold(hold, new_line):
	"""Update holds based on the new line.
	Returns: Updated holds."""
	return [True  if new_line[i] == '2' or (hold[i] and new_line[i] != '3') else False for i in range(10)]

def read_and_split_routine_stepf2(ssc, line_number):
	"""Read until the end of the notes of a stepf2 routine chart.
	Returns: left and right charts separated."""
	# Get first line.
	line, line_number = readLineUntilValid(ssc, line_number)

	print('Notes are starting in line {}: "{}".'.format(line_number, line))
	left, right = [], []
	l_hold = [False for _ in range(10)]
	r_hold = [False for _ in range(10)]
	while line[0] != ';':
		if line[0] == ',':
			left.append(line)
			right.append(line)
		else:
			# Process left.
			left_line = split_routine_stepf2_line(line, 'x', 'y', l_hold)
			l_hold = update_hold(l_hold, left_line)
			left.append(left_line)

			# Process right.
			right_line = split_routine_stepf2_line(line, 'y', 'x', r_hold)
			r_hold = update_hold(r_hold, right_line)
			right.append(right_line)

		line, line_number = readLineUntilValid(ssc, line_number)
	left.append(';\n')
	right.append(';\n')

	print(left)

	return left, right	

def is_routine_stepf2_line(line):
	""" Checks if a line is an indicator of a stepf2 routine chart."""
	return (len(line.split('\n')[0]) == 10
			and line[0] != ','
			and line[0] != '#'
			and ('x' in line
					or 'X' in line
					or 'y' in line
					or 'Y' in line))

def is_routine_stepf2_more_players_line(line):
	""" Checks if a line is an indicator of a stepf2 routine chart with more
	than two players."""
	return (len(line.split('\n')[0]) == 10
			and line[0] != ','
			and line[0] != '#'
			and ('z' in line
					or 'Z' in line))

def find_routines(ssc_filepath):
	""" Find all the routine charts in an ssc.
	Returns: A list of (description, chart_type) of the routine charts.
	"""
	ssc = open(ssc_filepath, 'r')
	routines = []

	line = ssc.readline()

	while line != '':
		# Chart description.
		description = ''
		
		# Chart steps type.
		steps_type = ''

		# Flag for whether the notes section started.
		notes_started = False

		while line != '' and not notes_started:
			# Check if the current line is a description line.
			if line.startswith('#DESCRIPTION'):
				description = line.split(':')[1].split(';')[0]

			# Check if the current line is a steps type line.
			if line.startswith('#STEPSTYPE'):
				steps_type = line.split(':')[1].split(';')[0]

			if line.startswith('#NOTES'):
				notes_started = True

			line = ssc.readline()

		# Flag for whether the notes section ended.
		notes_ended = False
		chart_type = 'stepmania'

		while line != '' and not notes_ended:
			if (chart_type == 'stepmania'
					and is_routine_stepf2_line(line)):
				chart_type = 'stepf2'

			if is_routine_stepf2_more_players_line(line):
				chart_type = 'stepf2more'

			if line[0] == ';':
				notes_ended = True

			line = ssc.readline()

		if (steps_type == 'pump-routine'
				or (steps_type == 'pump-double' and chart_type.startswith('stepf2'))):
			routines.append((description, chart_type))

	ssc.close()

	return routines


def split_routine(ssc_file, target_description, result_file, chart_type):
	""" Splits a routine chart from ssc_file that matches target_description
	and chart_type and writes variantes to result_file."""
	# Skip file header, which should be composed by configs of format "#something;".
	# Each config can be split in multiple lines.
	line, line_number = readLineUntilValid(ssc_file, 0)
	while True:
		# Check if file ended.
		if line == '':
			break

		# If it's not a config line, stop skipping.
		if line[0] != '#':
			break

		# Read multiple line configs.
		while line[-2] != ';':
			line, line_number = readLineUntilValid(ssc_file, line_number)

		# Get next line.
		line, line_number = readLineUntilValid(ssc_file, line_number, is_comment_invalid=False)

	print('Charts started in line {}.'.format(line_number))

	# Read through charts until the requested one is found.
	while True:
		# Check if file ended.
		if line == '':
			break

		# The first line of a chart should be like
		# "//------ pump-something something ------".
		assert(re.match(r'//-+\s*[a-zA-z0-9-]*-+', line),
			'Line "{}" is not a header start.'.format(line))
		print('New chart starting in line {}.'.format(line_number))

		header, description, steps_type = read_header(ssc_file, line_number)

		# Check if this is the correct chart.
		if (description.lower() != target_description.lower()
				or (chart_type == 'stepmania' and steps_type != 'pump-routine')
				or (chart_type == 'stepf2' and steps_type != 'pump-double')):
			# Skip the chart.
			while line[0] != ';':
				line, line_number = readLineUntilValid(ssc_file, line_number)

			line, line_number = readLineUntilValid(ssc_file, line_number, is_comment_invalid=False)
		else:
			print(header)
			
			left, right = (read_and_split_routine_stepmania(ssc_file, line_number)
					if chart_type == 'stepmania'
					else read_and_split_routine_stepf2(ssc_file, line_number))

			line, line_number = readLineUntilValid(ssc_file, line_number, is_comment_invalid=False)

			# Write left and right only charts.
			result_file.write(''.join(header).format(variation='P1', steps_type='pump-double'))
			result_file.write(''.join(left))

			result_file.write(''.join(header).format(variation='P2', steps_type='pump-double'))
			result_file.write(''.join(right))

			result_file.write(''.join(header).format(variation='F1', steps_type='pump-routine'))
			result_file.write((''.join(left)).replace(';',''))
			result_file.write('\n&\n')
			result_file.write(''.join(substitute(right, 'F')))

			result_file.write(''.join(header).format(variation='F2', steps_type='pump-routine'))
			result_file.write((''.join(substitute(left, 'F'))).replace(';',''))
			result_file.write('\n&\n')
			result_file.write(''.join(right))

			# result_file.write(''.join(header).format('ML'))
			# result_file.write(''.join(mirror(left)))

			# result_file.write(''.join(header).format('MR'))
			# result_file.write(''.join(mirror(right)))

			result_file.write(''.join(header).format(variation='M1', steps_type='pump-double'))
			result_file.write(''.join(addSub(left, right, 'M')))

			result_file.write(''.join(header).format(variation='M2', steps_type='pump-double'))
			result_file.write(''.join(addSub(right, left, 'M')))

			if chart_type != 'stepmania':
				result_file.write(''.join(header).format(variation='R', steps_type='pump-routine'))
				result_file.write(''.join(left))
				result_file.write('\n&\n')
				result_file.write(''.join(right))