import subprocess
from prevent_overwrite import prevent_overwrite

def make_analysis_comfile(design, sequence, gpr, comfile):
	"""Makes a comfile for creating an analysis file

	Inputs:
		design: path to the array design file
			This file should be named '*DNAFront_BCBottom*.tdt'
		sequence: path to the file that lists probe IDs and corresponding sequences
			This file should be named '*SequenceList*.txt')
		gpr: path to one of the *.gpr files associated with the array design
		comfile: path to the comfile to generate
	"""
	# Do not overwrite comfile if it already exists
	prevent_overwrite(comfile)
	# Open the comfile for writing
	with open(comfile, 'w') as f:
		f.write('perl /projectnb/siggers/perl_master/PBM/make_PBM_analysis_file.pl\n')
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
	subprocess.os.system('perl /project/siggers/perl/MISC/run_comfile_alert.pl -com ' +
			comfile + ' > ' + analysis)

