import subprocess
import glob
from prevent_overwrite import prevent_overwrite

def make_avg_gpr_list(avggprdirs, avgtype, outdir):
	"""Makes a file listing full paths of averaged gpr files at 488 and 647/635

	Inputs:
		avggprdirs: a list of the directories containing the averaged gpr files
		avgtype: the type of averaging that was performed; must be one of ('or', 'br', 'o1', 'o2')
			NOTE: averaging over orientations ('r') is separated here into 'o1' and 'o2'
		outdir: the directory in which to save the output list file
	
	Output:
		the path to the output list file
	"""
	# Use avgtype to determine file naming schema
	filename = ''
	if avgtype == 'or':
		filename = 'or_norm_madj*.gpr'
	if avgtype == 'br':
		filename = 'o1o2top_br_norm_madj*.gpr'
	if avgtype == 'o1':
		filename = 'o1match_r_norm_madj*.gpr'
	if avgtype == 'o2':
		filename = 'o2match_r_norm_madj*.gpr'
	# Make an empty list to store file paths
	files = []
	# Add files matching file naming schema from each directory in avggprdirs
	for avggprdir in avggprdirs:
		files += glob.glob(avggprdir + '/' + filename)
	# Sort file list
	files.sort()
	# Construct filename for output list
	avggprlist = outdir + '/' + avgtype + '_gpr.list'
	# Do not overwrite avggprlist if it already exists
	prevent_overwrite(avggprlist)
	# Open avggprlist for writing
	with open(avggprlist, 'w') as f:
		for filename in files:
			f.write(filename + '\n')
	# Return path to output list
	return(avggprlist)

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
	# Read contents of comfile as single string on one line
	with open(comfile) as f:
		comfilecont = f.read().replace('\n', ' ')
	# Run comfile
	print('qsub -sync y -P siggers -m a -cwd -N ' + avgtype + '_matrix -V -b y ' + comfilecont)
	subprocess.os.system('qsub -sync y -P siggers -m a -cwd -N ' + avgtype + '_matrix -V -b y ' + comfilecont)

def data_matrix_wrapper(avggprdirs, outdir, matprefix):
	"""Creates data matrices for each of the three averaging methods

	Inputs:
		avggprdirs: a list of the paths to the directories where the 488 and
			635/647 averaged gpr files are stored
		outdir: the path to the directory in which to save all new files
		matprefix: a prefix for the names of the data matrices
	"""
	# Make outdir
	subprocess.run(['mkdir', outdir])
	# Navigate to outdir after saving current working directory
	cwd = subprocess.os.getcwd()
	subprocess.os.chdir(outdir)
	# Make a data matrix for each of the four groups of averaged gpr files
	for avgtype in ['or', 'br', 'o1', 'o2']:
		# Make a list of all the averaged gpr files for this avgtype
		avggprlist = make_avg_gpr_list(avggprdirs, avgtype, outdir)
		# Construct path to comfile
		comfile = outdir + '/make_datamatrix_' + avgtype + '.com'
		# Construct path to output data matrix
		datmat = outdir + '/' + matprefix + '_' + avgtype + '.dat'
		# Make a comfile for making a data matrix 
		make_data_matrix_comfile(avggprlist, comfile, datmat)
		# Run data matrix comfile
		run_data_matrix_comfile(comfile, avgtype)
	# Navigate back to original working directory
	subprocess.os.chdir(cwd)


