import subprocess
import glob
from prevent_overwrite import prevent_overwrite

def to_488(gprdir):
	"""Converts the 635s and 647s to 488s in gpr files

	Inputs:
		gprdir: the path to the directory where the gpr files are stored
	"""
	# Save a list of all files in gprdir that end in ".gpr"
	files = glob.glob(gprdir + '/*.gpr')
	for filename in files:
		# Replace "635" and "647" with "488" if they follow "B" or "F" in each file
		subprocess.run(['sed', '-i', '-E', 's/(B|F)(635|647)/\\1488/g', filename])

def make_experiment_description(gprdir, expdesc):
	"""Makes an experiment description file

	Inputs:
		gprdir: the path to the directory where the gpr files are stored
			NOTE: This function assumes that all files in this directory ending
				in ".gpr" should be included in the experiment description file.
			NOTE: This function also assumes that all relevant files end in 
				"[0-9]-8.gpr" and can therefore be separated into chambers by
				looking at the last 7 characters of the filename
		expdesc: the path to the experiment description file to generate
	"""
	# Do not overwrite expdesc if it already exists
	prevent_overwrite(expdesc)
	# Navigate to gprdir after saving current directory
	cwd = subprocess.os.getcwd()
	subprocess.os.chdir(gprdir)
	# Save a sorted list of all files in gprdir that end in ".gpr"
	files = glob.glob('*.gpr')
	files.sort()
	# Navigate back to original directory (allows user to input relative paths)
	subprocess.os.chdir(cwd)
	# Store the possible file endings (chambers) in a set to get a unique list
	chamberset = set(filename[-7:] for filename in files)
	# Convert set to a list so it can be sorted
	chamberlist = list(chamberset)
	chamberlist.sort()
	# Open experiment description file for writing
	with open(expdesc, 'w') as f:
		for chamber in chamberlist:
			# Write the header for this chamber
			f.write('Pbm=1\nConcentration=100\nCy3=FOO\n')
			# Find all the file names matching this chamber and write to file
			matches = [filename for filename in files if chamber in filename]
			for match in matches:
				f.write(match + '\n')
			# Add an empty line between chambers
			f.write('\n')

def make_masliner_comfile(expdesc, comfile):
	"""Makes a comfile for running masliner

	Inputs:
		expdesc: the path to the experiment description file to use
		comfile: the path to the comfile to create
	"""
	# Do not overwrite comfile if it already exists
	prevent_overwrite(comfile)
	# Open file for writing
	with open(comfile, 'w') as f:
		f.write('perl /project/siggers/perl/GENEPIX/masliner_list.pl\n')
		f.write('-i ' + expdesc) 

def run_masliner_comfile(gprdir, comfile):
	"""Runs a comfile for running masliner

	Inputs:
		gprdir: the path to the directory where the gpr files are stored
		comfile: the path to the comfile to run
	"""
	# Navigate to gprdir after saving current directory
	cwd = subprocess.os.getcwd()
	subprocess.os.chdir(gprdir)
	# Read contents of comfile as single string on one line
	with open(comfile) as f:
		comfilecont = f.read().replace('\n', ' ')
	# Run comfile
	print('qsub -sync y -P siggers -m a -cwd -N masliner -V -b y ' + comfilecont)
	subprocess.os.system('qsub -sync y -P siggers -m a -cwd -N masliner -V -b y ' + comfilecont)
	# Navigate back to original directory
	subprocess.os.chdir(cwd)

def masliner_wrapper(gprdir, maslinerdir):
	"""Runs masliner on all gpr files in a given directory

	Inputs:
		gprdir: the path to the directory where the gpr files are saved
		maslinerdir: the path to the directory in which to save the output files
	"""
	# Get a list of all files in gprdir before running masliner
	beforefiles = glob.glob(gprdir + '/*')
	# If gprdir contains "635" or "647", change headers of gpr files
	if '635' or '647' in gprdir:
		to_488(gprdir)
	# Make experiment description file in gprdir
	expdesc = gprdir + '/experiment_description.txt'
	make_experiment_description(gprdir, expdesc)
	# Make masliner comfile in gprdir
	comfile = gprdir + '/masliner.com'
	make_masliner_comfile(expdesc, comfile)
	# Run masliner comfile
	run_masliner_comfile(gprdir, comfile)
	# Get a list of all files in gprdir after running masliner
	afterfiles = glob.glob(gprdir + '/*')
	# Get a list of all new files in gprdir
	newfiles = [filename for filename in afterfiles if filename not in beforefiles]
	# Make a new directory and move all new files to this directory
	subprocess.run(['mkdir', maslinerdir])
	for filename in newfiles:
		subprocess.run(['mv', filename, maslinerdir])

