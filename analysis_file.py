from subprocess import os

def make_analysis_comfile(design, sequence, gpr, comfile):
	"""Generates comfile for making analysis file

	Inputs:
		design: array design file name
			e.g. ENH_TILE_001_085605_D_DNAFront_BCBottom_20180616.tdt
		sequence: file name of list of probe IDs and corresponding sequences
			e.g. ENH_TILE_001_085605_D_SequenceList_20180616.txt
		gpr: file name of one of the *.gpr files associated with the array design
			e.g. 258560610008_G600_488_1-8.gpr
		comfile: the name (path) of the comfile to generate
			e.g. make_analysis_file.com
	"""
	# Open the comfile for writing
	with open(comfile, 'w') as f:
		f.write('perl /projectnb/siggers/perl_master/PBM/make_PBM_analysis_file.pl\n')
		f.write('-i ' + design + '\n')
		f.write('-j ' + sequence + '\n')
		f.write('-g ' + gpr)

def run_analysis_comfile(comfile, analysis_file):
	"""Runs comfile for making analysis file

	Inputs:
		comfile: the name (path) of the comfile to run
			e.g. make_analysis_file.com
		analysis_file: the name (path) of the analysis file to generate
			e.g. ID_085605_Genomic_analysis.txt
	"""
	# Execute the perl script that runs the comfile
	# Redirect output to analysis_file
	os.system('perl /project/siggers/perl/MISC/run_comfile_alert.pl -com ' +
			comfile + ' > ' + analysis_file)

