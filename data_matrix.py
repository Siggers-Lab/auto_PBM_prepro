import glob
import subprocess
from prevent_overwrite import prevent_overwrite

def make_avg_gpr_list(avggprdirs, avgtype, outdir):
	"""Makes a file listing full paths of averaged gpr files

	Inputs:
		avggprdirs: a list of the directories containing the averaged gpr files
		avgtype: the type of averaging that was performed; must be one of ('or', 'br', 'r')
		outdir: the directory in which to save the output list file
	"""
	# Use avgtype to determine file naming schema
	filename = ''
	if avgtype == 'or':
		filename = 'or_norm_madj*.gpr'
	if avgtype == 'br':
		filename = 'o1o2top_br_norm_madj*.gpr'
	if avgtype == 'r':
		filename = 'o[1,2]match_r_norm_madj*.gpr'
	# Make an empty list to store file paths
	files = []
	# Add files matching file naming schema from each directory in avggprdirs
	for avggprdir in avggprdirs:
		files += glob.glob(avggprdir + '/' + filename)
	files.sort()
	# Write output file for 'or' and 'br' options
	if avgtype in ['or', 'br']:
		# Do not overwrite file if it already exists
		prevent_overwrite(outdir + '/' + avgtype + '_gpr.list')
		# Open file for writing
		with open(outdir + '/' + avgtype + '_gpr.list', 'w') as f:
			for filename in files:
				f.write(filename + '\n')
	# Write two output files for 'r' option
	elif avgtype == 'r':
		# Sort files into o1 and o2 groups
		o1 = [filename for filename in files if 'o1match' in filename]
		o2 = [filename for filename in files if 'o2match' in filename]
		# Do not overwrite files if they already exist
		prevent_overwrite(outdir + '/o1_gpr.list')
		prevent_overwrite(outdir + '/o2_gpr.list')
		# Write list of o1 files
		with open(outdir + '/o1_gpr.list', 'w') as f:
			for filename in o1:
				f.write(filename + '\n')
		# Write list of o2 files
		with open(outdir + '/o2_gpr.list', 'w') as f:
			for filename in o2:
				f.write(filename + '\n')

def make_data_matrix_comfile(avggprlist, comfile, datmat):
	"""Makes a comfile for creating a data matrix

	Inputs:
		avggprlist: the path to the file listing the averaged gpr files
		comfile: the path to the output comfile
		datmat: the path to the data matrix you want to generate
	"""
	# Do not overwrite comfile if it already exists
	prevent_overwrite(comfile)
	# Do not overwrite datmat if it already exists
	# NOTE: this function does not actually write to datmat, but this is where
	#	the filename is chosen
	prevent_overwrite(datmat)
	# Open comfile for writing
	with open(comfile, 'w') as f:
		f.write('perl /project/siggers/perl/GENEPIX/control_sequence_process.pl\n\n')
		f.write('-l ' + avggprlist + '\n')
		f.write('-o ' + datmat)

def run_data_matrix_comfile(comfile, avgtype):
	"""Runs a comfile for creating a data matrix

	Inputs:
		comfile: the comfile to run
		avgtype: the type of averaging that was done; must be one of ('or', 'br', 'r')
			This affects the names of the error and output files
	"""
	# NOTE: Change the path to run_comfile_alert.pl at some point maybe???
	subprocess.os.system('perl /projectnb/siggers/data/rebekah_project/run_comfile_alert.pl -com ' +
			comfile + ' -qsub ' + avgtype + 'matrix')




