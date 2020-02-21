import subprocess
import glob
from prevent_overwrite import prevent_overwrite

def make_norm_gpr_list(normgprdir, normgprlist):
	"""Makes a file listing all the normalized, masliner adjusted gpr files

	Inputs:
		normgprdir: the path to the directory containing the normalized,
			masliner adjusted gpr files
			NOTE: This assumes that all files of the form 'norm_madj*.gpr'
				should be included
		normgprlist: the path to the output list file
	"""
	# Do not overwrite normgprlist if it already exists
	prevent_overwrite(normgprlist)
	# Get full paths to all files in normgprdir of the form 'norm_madj*.gpr'
	files = glob.glob(normgprdir + '/norm_madj*.gpr')
	files.sort()
	# Write list to normgprlist
	with open(normgprlist, 'w') as f:
		for filename in files:
			f.write(filename + '\n')

def make_average_probes_comfile(normgprlist, avgtype, comfile):
	"""Makes a comfile for averaging probe intensities

	Inputs:
		normgprlist: the path to the file listing the normalized, masliner
			adjusted gpr files
		avgtype: the type of averaging to perform; must be one of ('or', 'br', 'r')
		comfile: the path to the output comfile to write
	"""
	# Do not overwrite comfile if it already exists
	prevent_overwrite(comfile)
	# Open comfile for writing
	with open(comfile, 'w') as f:
		f.write('perl /project/siggers/perl/GENEPIX/average_replicate_rc_custom_probes.pl\n\n')
		f.write('-l ' + normgprlist + '\n')
		f.write('-op ' + avgtype + '\n')
		f.write('-avg ' + avgtype + '\n')
		f.write('-no_gfilter')

def run_average_probes_comfile(comfile, avgtype):
	"""Runs a comfile for averaging probe intensities

	Inputs:
		comfile: the comfile to run
		avgtype: the type of averaging to perform; must be one of ('or', 'br', 'r')
			This affects the names of the output and error files for this job
	"""
	# Run the comfile
	# NOTE: change the path to run_comfile_alert.pl eventually maybe
	subprocess.os.system('perl /projectnb/siggers/data/rebekah_project/run_comfile_alert.pl -com ' +
			comfile + ' -qsub avg_' + avgtype)



