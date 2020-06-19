import subprocess
import glob
import logging
from natsort import natsorted
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
    files = natsorted(files)

    # Navigate back to original directory
    subprocess.os.chdir(cwd)

    # Store the possible file endings (chambers) in a set to get a unique list
    chamberset = set(filename[-7:] for filename in files)

    # Convert chamberset to a sorted list
    chamberlist = natsorted(list(chamberset))

    # Initialize a list to store the highest intensity scan for each chamber
    highintfiles = []

    # Find highest intensity scan for each chamber
    for chamber in chamberlist:
        # Find all files for this chamber
        matches = [filename for filename in files if chamber in filename]

        # The files are sorted, so the last one should be the highest intensity
        highintfiles.append(matches[-1])

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
        f.write('perl /project/siggers/perl/GENEPIX/' +
                'gpr_file_process_conc_series.pl\n')
        f.write('-i ' + madjgprlist + '\n')
        f.write('-a ' + analysisfile + '\n')
        f.write('-keep_ctrl\n-output_norm_files\n-o norm\n-f1med')


def run_spatial_detrend_comfile(comfile, madjgprdir):
    """Runs a comfile for performing spatial detrending

    Inputs:
        comfile: the path to the comfile to run
        madjgprdir: the path to the directory in which the masliner adjusted
            gpr files are stored
    """
    # Navigate to madjgprdir after saving current working directory
    cwd = subprocess.os.getcwd()
    subprocess.os.chdir(madjgprdir)

    # Read contents of comfile as single string on one line
    with open(comfile) as f:
        comfilecont = f.read().replace('\n', ' ')

    # Run comfile
    logging.info('qsub -sync y -P siggers -m a -cwd -N customprobes -V -b y ' +
            comfilecont)
    subprocess.run(['qsub', '-sync', 'y', '-P', 'siggers', '-m', 'a', '-cwd',
        '-N', 'customprobes', '-V', '-b', 'y', comfilecont])

    # Navigate back to original directory
    subprocess.os.chdir(cwd)


def spatial_detrend_wrapper(madjgprdir, analysisfile, normgprdir):
    """Runs spatial detrending on all masliner adjusted gpr files in a directory

    Inputs:
        madjgprdir: the path to the directory containing the masliner adjusted
            gpr files to use
        analysisfile: the path to the analysis file to use
        normgprdir: the path to the directory in which to save the output files
    """
    # If normgprdir already exists, abort to prevent overwrite
    prevent_overwrite(normgprdir)

    # Get a list of all files in madjgprdir before spatial detrending
    beforefiles = glob.glob(madjgprdir + '/*')

    # Make a file listing all the masliner adjusted gpr files in madjgprdir
    logging.info('Making a list of all masliner adjusted gpr files')
    madjgprlist = madjgprdir + '/madj_gpr.list'
    make_madj_gpr_list(madjgprdir, madjgprlist)

    # Make a comfile for performing spatial detrending in madjgprdir
    logging.info('Making spatial detrend comfile')
    comfile = madjgprdir + '/process_custom_probes.com'
    make_spatial_detrend_comfile(madjgprlist, analysisfile, comfile)

    # Run spatial detrending comfile
    logging.info('Running spatial detrend comfile ' +
            '(this may take a few minutes)')
    run_spatial_detrend_comfile(comfile, madjgprdir)

    # Get a list of all files in madjgprdir after spatial detrending
    afterfiles = glob.glob(madjgprdir + '/*')

    # Get a list of all new files in madjgprdir
    newfiles = [filename for filename in afterfiles
            if filename not in beforefiles]

    # Make a new directory and move all new files to this directory
    subprocess.run(['mkdir', normgprdir])
    logging.info('Moving files to normalized gpr directory: ' +
            normgprdir + '\n')
    for filename in newfiles:
        subprocess.run(['mv', filename, normgprdir])


