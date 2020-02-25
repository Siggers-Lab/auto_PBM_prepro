import analysis_file
import masliner
import spatial_detrend
import average_probes
import data_matrix
import argparse

def run_pipeline(analysisdir, gpr488dir, gpr647dir, outdir, matprefix):
	"""Wrapper that runs the full PBM preprocessing pipeline

	Inputs:
		analysisdir: the path to the directory where the analysis file is stored
			OR the path to the directory where a new analysis file should be made
			In the latter case, this directory must contain three files:
				*DNAFront_BCBottom*.tdt
				*SequenceList*.txt
				*.gpr
		gpr488dir: the path to the directory containing the gpr files run at a wavelength of 488
		gpr647dir: the path to the directory containing the gpr files run at a wavelength of 635/647
		outdir: the path to the directory where the output data matrices should be saved
		matprefix: the prefix to add to the filenames of the output data matrices
	"""
	# Check for analysis file and create one if necessary
	# Save path to analysis file
	analysisfile = analysis_file.analysis_file_wrapper(analysisdir)

	# Run masliner on 488 files
	madjgpr488dir = gpr488dir + '/masliner'
	masliner.masliner_wrapper(gpr488dir, madjgpr488dir)
	# Run masliner on 635/647 files
	madjgpr647dir = gpr647dir + '/masliner'
	masliner.masliner_wrapper(gpr647dir, madjgpr647dir)

	# Perform spatial detrending on 488 files
	normgpr488dir = gpr488dir + '/spatial_detrend'
	spatial_detrend.spatial_detrend_wrapper(madjgpr488dir, analysisfile, normgpr488dir)
	# Perform spatial detrending on 635/647 files
	normgpr647dir = gpr647dir + '/spatial_detrend'
	spatial_detrend.spatial_detrend_wrapper(madjgpr647dir, analysisfile, normgpr647dir)
	
	# Average probe intensities for 488 files
	avggpr488dir = gpr488dir + '/average_probes'
	average_probes.average_probes_wrapper(normgpr488dir, avggpr488dir)
	# Average probe intensities for 635/647 files
	avggpr647dir = gpr647dir + '/average_probes'
	average_probes.average_probes_wrapper(normgpr647dir, avggpr647dir)

	# Create data matrices
	avggprdirs = [avggpr488dir, avggpr647dir]
	data_matrix.data_matrix_wrapper(avggprdirs, outdir, matprefix)

# Create object for handling command line arguments
parser = argparse.ArgumentParser(description = 'Pipeline for preprocessing PBM data') #,
		#usage = 'python preprocess_pipeline.py -a <analysis_directory>')
parser.add_argument('analysis_dir',
		help = 'the absolute path to the directory where the analysis file is saved or should be created')
parser.add_argument('gpr_dirs', nargs = 2,
		help = 'the absolute paths to the two directories (488 and 635/647) where the gpr files are saved')
parser.add_argument('output_dir',
		help = 'the absolute path to the directory where the output data matrices should be saved')
parser.add_argument('-p', '-prefix', default = '',
		help = 'the prefix to add to the filenames for the output data matrices')
# Parse out arguments
args = parser.parse_args()
# Call pipeline wrapper function on command line arguments
run_pipeline(args.analysis_dir, args.gpr_dirs[0], args.gpr_dirs[1], args.output_dir, args.p)





