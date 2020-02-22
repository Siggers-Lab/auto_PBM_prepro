import subprocess
import glob
from prevent_overwrite import prevent_overwrite

def make_madj_gpr_list(madjgprdir, madjgprlist):
	"""Makes a list of all masliner adjusted gpr files at highest scan intensity

	Inputs:
		madjgprdir: the directory where the masliner adjusted gpr files are
			NOTE: assumes that all files of the form "madj*.gpr" in this
				directory should be used
			madjgprlist: the path to the output list file
	"""
	# Do not overwrite madjgprlist if it already exists
	prevent_overwrite(madjgprlist)
	# Navigate to madjgprdir after saving current working directory
	cwd = subprocess.os.getcwd()
	subprocess.os.chdir(madjgprdir)
	# Get a list of all masliner adjusted gpr files and make sure they're sorted
	files = glob.glob("madj*.gpr")
	files.sort()
	# Navigate back to original directory (allows relative paths)
	subprocess.os.chdir(cwd)
	# The last file in the list should be at the highest scan intensity
	# Extract the main filename of this last file (everything except #-8.gpr)
	highint = files[-1][:-7]
	# Find all filenames matching the main part of this filename
	highintfiles = [filename for filename in files if highint in filename]
	# Write list to madjgprlist
	with open(madjgprlist, 'w') as f:
		for filename in highintfiles:
			f.write(filename + '\n')

def make_spatial_detrend_comfile(madjgprlist, analysisfile, comfile):
	"""Makes a comfile for performing spatial detrending
	
	Inputs:
		madjgprlist: the path to the list of masliner adjusted gpr files
		analysisfile: the path to the analysis file
		comfile: the path to the output comfile
	"""
	# Do not overwrite comfile if it already exists
	prevent_overwrite(comfile)
	# Open comfile for writing
	with open(comfile, 'w') as f:
		f.write('perl /project/siggers/perl/GENEPIX/gpr_file_process_conc_series.pl\n')
		f.write('-i ' + madjgprlist + '\n')
		f.write('-a ' + analysisfile + '\n')
		f.write('-keep_ctrl\n-output_norm_files\n-o norm\n-f1med')

def run_spatial_detrend_comfile(comfile, madjgprdir):
	"""Runs a comfile for performing spatial detrending
	
	Inputs:
		comfile: the path to the comfile to run
		madjgprdir: the directory where the masliner adjusted gpr files are stored
	"""
	# Navigate to madjgprdir after saving current working directory
	cwd = subprocess.os.getcwd()
	subprocess.os.chdir(madjgprdir)
	# NOTE: Change run_comfile_alert.pl path maybe?
	subprocess.os.system('perl /projectnb/siggers/data/rebekah_project/run_comfile_alert.pl -com ' +
			comfile + ' -qsub customprobes')
	# Navigate back to original directory
	subprocess.os.chdir(cwd)

def spatial_detrend_wrapper(madjgprdir, analysisfile, normgprdir):
	"""Performs spatial detrending on all masliner adjusted gpr files in a directory
	
	Inputs:
		madjgprdir: the path to the directory containing the masliner adjusted
			gpr files to use
		analysisfile: the path to the analysis file to use
		normgprdir: the path to the directory in which to save the output files
	"""
	# Get a list of all files in madjgprdir before spatial detrending
	beforefiles = glob.glob(madjgprdir + '/*')
	# Make a file listing all the masliner adjusted gpr files to use in madjgprdir
	madjgprlist = madjgprdir + '/madj_gpr.list'
	make_madj_gpr_list(madjgprdir, madjgprlist)
	# Make a comfile for performing spatial detrending in madjgprdir
	comfile = madjgprdir + '/process_custom_probes.com'
	make_spatial_detrend_comfile(madjgprlist, analysisfile, comfile)
	# Run spatial detrending comfile
	run_spatial_detrend_comfile(comfile, madjgprdir)
	# Get a list of all files in madjgprdir after spatial detrending
	afterfiles = glob.glob(madjgprdir + '/*')
	# Get a list of all new files in madjgprdir
	newfiles = [filename for filename in afterfiles if filename not in beforefiles]
	# Make a new directory and move all new files to this directory
	subprocess.run(['mkdir', normgprdir])
	for filename in newfiles:
		subprocess.run(['mv', filename, normgprdir])






