import subprocess
import glob
import logging
from prevent_overwrite import prevent_overwrite

def check_analysis_file(analysisdir):
	"""Checks if there is an analysis file in a given directory

	Inputs:
		analysisdir: the directory to check for an analysis file
	
	Output:
		If there is already one analysis file in the directory:
			the path to the analysis file
		If there is no analysis file in the directory:
			the path to the "*DNAFront_BCBottom*.tdt" file in the directory
			the path to the "*SequenceList*.txt" file in the directory
			the path to a "*.gpr" file in the directory
	"""
	# Check for a file in analysisdir of the form "*analysis*.txt"
	analysisfile = glob.glob(analysisdir + '/*analysis*.txt')
	# If no files match, check for files needed to make new analysis file
	if len(analysisfile) < 1:
		design = glob.glob(analysisdir + '/*DNAFront_BCBottom*.tdt')
		sequence = glob.glob(analysisdir + '/*SequenceList*.txt')
		gpr = glob.glob(analysisdir + '/*.gpr')
		# Make sure there is exactly one file for each of design and sequence
		if len(design) > 1:
			logging.error('There is more than one file of the form ' +
					'"*DNAFront_BCBottom*.tdt" in ' + analysisdir +
					'\nPlease remove extra files and try again')
			raise FileExistsError('There is more than one file of the form ' +
					'"*DNAFront_BCBottom*.tdt" in ' + analysisdir +
					'\nPlease remove extra files and try again')
		if len(sequence) > 1:
			logging.error('There is more than one file of the form ' +
					'"*SequenceList*.txt" in ' + analysisdir +
					'\nPlease remove extra files and try again')
			raise FileExistsError('There is more than one file of the form ' +
					'"*SequenceList*.txt" in ' + analysisdir +
					'\nPlease remove extra files and try again')
		if len(design) < 1:
			logging.error('There is no file of the form ' +
					'"*DNAFront_BCBottom*.tdt" in ' + analysisdir +
					'\nPlease make sure such a file exists and try again')
			raise FileNotFoundError('There is no file of the form ' +
					'"*DNAFront_BCBottom*.tdt" in ' + analysisdir +
					'\nPlease make sure such a file exists and try again')
		if len(sequence) < 1:
			logging.error('There is no file of the form ' +
					'"*SequenceList*.txt" in ' + analysisdir +
					'\nPlease make sure such a file exists and try again')
			raise FileNotFoundError('There is no file of the form ' +
					'"*SequenceList*.txt" in ' + analysisdir +
					'\nPlease make sure such a file exists and try again')
		# Make sure there is at least one gpr file
		if len(gpr) < 1:
			logging.error('There is no file of the form ' +
					'"*.gpr" in ' + analysisdir +
					'\nPlease make sure such a file exists and try again')
			raise FileNotFoundError('There is no file of the form ' +
					'"*.gpr" in ' + analysisdir +
					'\nPlease make sure such a file exists and try again')
		# If there is more than 1 gpr file, tell user which one is being used
		if len(gpr) > 1:
			logging.info('There is more than one file of the form ' +
					'"*.gpr" in ' + analysisdir + '\nUsing ' + gpr[0])
		# If all the files exist, return their paths
		return([design[0], sequence[0], gpr[0]])
	# If exactly one file matches the analysis file pattern, return its path
	elif len(analysisfile) == 1:
		return(analysisfile)
	# If more than one file matches the analysis file pattern, abort
	else:
		logging.error('There is more than one file of the form ' +
				'"*analysis*.txt" in ' + analysisdir +
				'\nPlease remove extra files and try again')
		raise FileExistsError('There is more than one file of the form ' +
				'"*analysis*.txt" in ' + analysisdir +
				'\nPlease remove extra files and try again')

def make_analysis_comfile(design, sequence, gpr, comfile):
	"""Makes a comfile for creating an analysis file

	Inputs:
		design: path to the array design file
			This file should be named '*DNAFront_BCBottom*.tdt'
		sequence: path to the file that lists probe IDs with their sequences
			This file should be named '*SequenceList*.txt')
		gpr: path to one of the *.gpr files associated with the array design
		comfile: path to the comfile to generate
	"""
	# Do not overwrite comfile if it already exists
	prevent_overwrite(comfile)
	# Open the comfile for writing
	with open(comfile, 'w') as f:
		f.write('perl /projectnb/siggers/perl_master/PBM/' +
				'make_PBM_analysis_file.pl\n')
		f.write('-i ' + design + '\n')
		f.write('-j ' + sequence + '\n')
		f.write('-g ' + gpr)

def run_analysis_comfile(comfile, analysis):
	"""Runs a comfile for creating an analysis file

	Inputs:
		comfile: the path to the comfile to run
		analysis: the path to the analysis file to create
	"""
	# Do not overwrite analysis if it already exists
	prevent_overwrite(analysis)
	# Run the comfile and redirect the output to analysis_file
	with open(analysis, 'w') as f:
		subprocess.run(['perl',
			'/project/siggers/perl/MISC/run_comfile_alert.pl', '-com',
			comfile], stdout = f)

def analysis_file_wrapper(analysisdir):
	"""Checks for an analysis file and creates one if it doesn't exist

	Inputs:
		analysisdir: the directory to check for an analysis file
	
	Output:
		the path to the analysis file (that may be newly created)
	"""
	# Check if there is an analysis file in analysisdir
	logging.info('Checking for analysis file')
	analysis = check_analysis_file(analysisdir)
	# If length of analysis is 3, then make a new analysis file
	if len(analysis) == 3:
		logging.info('Making new analysis file')
		# Make analysis comfile
		analysiscom = analysisdir + '/make_analysis_file.com'
		make_analysis_comfile(analysis[0], analysis[1],
				analysis[2], analysiscom)
		# Extract ID number from filename of design file
		endID = analysis[0].index('_D_DNAFront_BCBottom')
		startID = analysis[0].rindex('_', 0, endID) + 1
		ID = analysis[0][startID:endID]
		# Construct analysis file name
		analysisfile = analysisdir + '/ID_' + ID + '_genomic_analysis.txt'
		# Run analysis comfile
		run_analysis_comfile(analysiscom, analysisfile)
		# Return analysis file name
		logging.info('Made analysis file: ' + analysisfile + '\n')
		return(analysisfile)
	# If length of analysis is 1, then there's already an analysis file
	elif len(analysis) == 1:
		logging.info('Found analysis file: ' + analysis[0] + '\n')
		# Return analysis file name
		return(analysis[0])
