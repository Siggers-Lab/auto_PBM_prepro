import subprocess
import glob

def make_experiment_description(gprdir, exp_desc):
	"""Generates experiment description file

	Inputs:
		gprdir: the path to the directory where the gpr files are saved
			e.g. /projectnb/siggers/pbmdata/gpr/Recruitome/v2_array/258566410001/488_scan/
			NOTE: this function assumes that all files in this directory ending
				in ".gpr" should be included in the experiment description file
		exp_desc: the name (path) of the experiment description file to generate
			e.g. ./experiment_description.txt
	"""
	# Navigate to gprdir after saving current directory
	cwd = subprocess.os.getcwd()
	subprocess.os.chdir(gprdir)
	# Save a sorted list of all files in gprdir that end in ".gpr"
	files = glob.glob('*.gpr')
	files.sort()
	# Navigate back to original directory (allows user to input relative paths)
	subprocess.os.chdir(cwd)
	# Store the possible file endings (chambers) in a set to get a unique list
	# NOTE: this assumes the file names end in '#-8.gpr'
	chamber_set = set(filename[-7:] for filename in files)
	# Convert set to a list so it can be sorted
	chamber_list = list(chamber_set)
	chamber_list.sort()
	# Open experiment description file for writing
	with open(exp_desc, 'w') as f:
		for chamber in chamber_list:
			# Write the header for this chamber
			f.write('Pbm=1\nConcentration=100\nCy3=FOO\n')
			# Find all the file names matching this chamber and write to file
			matches = [filename for filename in files if chamber in filename]
			for match in matches:
				f.write(match + '\n')
			# Add an empty line between chambers
			f.write('\n')

def make_masliner_comfile(exp_desc, comfile):
	"""Generates comfile for running masliner

	Inputs:
		exp_desc: the name (path) of the experiment description file to use
		comfile: the name (path) of the comfile to generate
	"""
	# Open file for writing
	with open(comfile, 'w') as f:
		f.write('perl /project/siggers/perl/GENEPIX/masliner_list.pl\n')
		f.write('-i ' + exp_desc) 

def run_masliner_comfile(gprdir, comfile):
	"""Runs comfile for running masliner

	Inputs:
		 gprdir: the path to the directory where the gpr files are saved
		 	e.g. /projectnb/siggers/pbmdata/gpr/Recruitome/v2_array/258566410001/488_scan/
		comfile: the ABSOLUTE path to the comfile to run
	"""
	# NOTE: update run_comfile_alert.pl path after -P option updated!!
	# Navigate to gprdir after saving current directory
	cwd = subprocess.os.getcwd()
	subprocess.os.chdir(gprdir)
	# Run masliner comfile
	subprocess.os.system('perl /projectnb/siggers/data/rebekah_project/run_comfile_alert.pl -com ' +
			comfile + ' -qsub masliner')
	# Navigate back to original directory
	subprocess.os.chdir(cwd)




