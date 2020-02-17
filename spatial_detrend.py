import subprocess
import glob

def make_madj_gpr_list(madjgprdir, madjgprlist):
    """Makes a list of all masliner adjusted gpr files at highest scan intensity

    Inputs:
        madjgprdir: the directory where the masliner adjusted gpr files are
            NOTE: assumes that all files of the form "madj*.gpr" in this
                directory should be used
        madjgprlist: the name (path) of the output file
    """
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
    hi_int = files[-1][:-7]
    # Find all filenames matching the main part of this filename
    hi_int_files = [filename for filename in files if hi_int in filename]
    # Write list to madjgprlist
    with open(madjgprlist, 'w') as f:
        for filename in hi_int_files:
            f.write(filename + '\n')

def make_spatial_detrend_comfile(madjgprlist, analysisfile, comfile):
    """Makes a comfile for running the spatial detrending process

    Inputs:
       madjgprlist: the name (path) of the list of masliner adjusted gpr files
       analysisfile: the name (path) of the analysis file
       comfile: the name (path) of the output comfile
    """
    # Open comfile for writing
    with open(comfile, 'w') as f:
        f.write('perl /project/siggers/perl/GENEPIX/gpr_file_process_conc_series.pl\n')
        f.write('-i ' + madjgprlist + '\n')
        f.write('-a ' + analysisfile + '\n')
        f.write('-keep_ctrl\n-output_norm_files\n-o norm\n-f1med')

def run_spatial_detrend_comfile(comfile, madjgprdir):
    """Runs the comfile that performs spatial detrending

    Inputs:
        comfile: the name (path) of the comfile to run
        madjgprdir: the directory where the masliner adjusted gpr files are
    """
    # Navigate to madjgprdir after saving current working directory
    cwd = subprocess.os.getcwd()
    subprocess.os.chdir(madjgprdir)
    # NOTE: Change run_comfile_alert.pl path!!
    subprocess.os.system('perl /projectnb/siggers/data/rebekah_project/run_comfile_alert.pl -com ' +
            comfile + ' -qsub customprobes')
    # Navigate back to original directory
    subprocess.os.chdir(cwd)


