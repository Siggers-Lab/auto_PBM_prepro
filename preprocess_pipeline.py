import subprocess
import analysis_file
import masliner
import spatial_detrend
import average_probes
import data_matrix
import argparse
import logging
import sys
from prevent_overwrite import prevent_overwrite

# Make sure Python 3 is being used
if sys.version_info[0] != 3:
    print("This script requires Python version 3!\n" +
            "Please run the following command and then try again:\n" +
            "module load python3")
    sys.exit(1)

def run_pipeline(analysisdir, gprdirs, outdir, matprefix):
    """Wrapper that runs the full PBM preprocessing pipeline

    Inputs:
        analysisdir: the path to the directory where the analysis file is stored
            OR the path to the directory where a new analysis file should be made
            In the latter case, this directory must contain three files:
                *DNAFront_BCBottom*.tdt
                *SequenceList*.txt
                *.gpr
        gprdirs: a list of the paths to the directories containing the gpr files
        outdir: the path to the directory where the output data matrices should be saved
        matprefix: the prefix to add to the filenames of the output data matrices
    """
    # Create outdir if it doesn't already exist
    if not subprocess.os.path.exists(outdir):
        subprocess.run(['mkdir', outdir])
    
    # Create a logfile to track progress and errors
    logfile = outdir + '/' + matprefix + '_logfile'
    
    # Do not overwrite logfile if it already exists
    prevent_overwrite(logfile)
    
    # Configure logging settings
    logging.basicConfig(filename = logfile, level = logging.INFO,
            format = '%(levelname)s:%(message)s')

    # Check for analysis file and create one if necessary
    # Save path to analysis file
    analysisfile = analysis_file.analysis_file_wrapper(analysisdir)

    # Run masliner
    madjgprdirs = [gprdir + '/masliner' for gprdir in gprdirs]
    for i in range(len(gprdirs)):
        masliner.masliner_wrapper(gprdirs[i], madjgprdirs[i])

    # Perform spatial detrending
    normgprdirs = [gprdir + '/spatial_detrend' for gprdir in gprdirs]
    for i in range(len(gprdirs)):
        spatial_detrend.spatial_detrend_wrapper(madjgprdirs[i], analysisfile,
                normgprdirs[i])
    
    # Average probe intensities
    avggprdirs = [gprdir + '/average_probes' for gprdir in gprdirs]
    for i in range(len(gprdirs)):
        average_probes.average_probes_wrapper(normgprdirs[i], avggprdirs[i])

    # Create data matrices
    data_matrix.data_matrix_wrapper(avggprdirs, outdir, matprefix)


# Create object for handling command line arguments
# Setting add_help to False allows required arguments to be printed before
#   optional arguments in help message
parser = argparse.ArgumentParser(add_help = False,
        description = 'Pipeline for preprocessing PBM data',
        usage = 'python preprocess_pipeline.py -a ANALYSIS_DIR ' +
        '-g GPR_DIRS [GPR_DIRS ...] -o OUTPUT_DIR -p PREFIX [-h]')

# Add groups for both required and optional arguments
requiredargs = parser.add_argument_group('required arguments')
optionalargs = parser.add_argument_group('optional arguments')

# Add required argument for analysis directory
requiredargs.add_argument('-a', '--analysis_dir', required = True,
        help = 'the absolute path to the directory where the analysis file ' +
        'is saved or should be created. NOTE: The analysis file must be of ' +
        'the form *analysis*.txt. If the analysis file does not already ' +
        'exist, this directory must contain the three files necessary to ' +
        'create a new analysis file: *DNAfront_BCBottom*.txt, ' +
        '*SequenceList*.txt, and *.gpr')

# Add required argument for gpr directory or directories
requiredargs.add_argument('-g', '--gpr_dirs', required = True, nargs = '+',
        help = 'the absolute paths to the directory or directories ' +
        'where the gpr files are saved')

# Add required argument for output directory
requiredargs.add_argument('-o', '--output_dir', required = True,
        help = 'the absolute path to the directory where the output data ' +
        'matrices should be saved')

# Add required argument for data matrix filename prefix
requiredargs.add_argument('-p', '--prefix', required = True,
        help = 'the prefix to add to the filenames of the output data matrices')

# Add optional help argument back in
optionalargs.add_argument('-h', '--help', action = 'help',
        default = argparse.SUPPRESS, help = 'show this help message and exit')

# Parse out arguments
args = parser.parse_args()

# Call pipeline wrapper function on arguments
run_pipeline(args.analysis_dir, args.gpr_dirs, args.output_dir, args.prefix)


