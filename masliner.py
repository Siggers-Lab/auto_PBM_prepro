import subprocess
import glob
import logging
from natsort import natsorted
from collections import Counter
from prevent_overwrite import prevent_overwrite

def to_488(gprdir):
    """Converts the 635s and 647s to 488s in gpr files

    Inputs:
        gprdir: the path to the directory where the gpr files are stored
    """
    # Save a list of all files in gprdir that end in ".gpr"
    files = glob.glob(gprdir + '/*.gpr')
    for filename in files:
        # Replace "635" and "647" with "488" if they follow "B" or "F"
        subprocess.run(['sed', '-i', '-E', 's/(B|F)(635|647)/\\1488/g',
            filename])


def make_experiment_description(gprdir, exclude):
    """Makes experiment description file(s)

    Inputs:
        gprdir: the path to the directory where the gpr files are stored
            NOTE: This function assumes that all files in this directory ending
                in ".gpr" (except those listed in exclude) should be included
                in the experiment description file
            NOTE: This function also assumes that all relevant files end in 
                "[0-9]-8.gpr" and can therefore be separated into chambers by
                looking at the last 7 characters of the filename
        exclude: a list of files to exclude from the experiment description file

    Output:
        a list of all the experiment description files generated
    """
    # Navigate to gprdir after saving current directory
    cwd = subprocess.os.getcwd()
    subprocess.os.chdir(gprdir)

    # Save a sorted list of all files in gprdir that end in ".gpr"
    files = glob.glob('*.gpr')
    files = natsorted(files)

    # Remove exclude from files
    if exclude is not None:
        files = [filename for filename in files if filename not in exclude]

    # Navigate back to original directory
    subprocess.os.chdir(cwd)

    # Store the possible file endings (chambers) in a set to get a unique list
    chamberset = set(filename[-7:] for filename in files)

    # Make a dictionary to group the chambers by which files are used
    chamberdict = {}
    for chamber in chamberset:
        # Collapse the filenames into a string
        filenames = ''.join([filename[:-7] for filename in files
            if chamber in filename])

        # If filenames is already in the dictionary, add chamber to its value
        if filenames in chamberdict:
            chamberdict[filenames].append(chamber)

        # Otherwise add filenames as a key with chamber as its value
        else:
            chamberdict[filenames] = [chamber]

    # Initialize an array to store the experiment description filenames
    expdescs = []

    # Loop through the values in chamberdict
    for chamberlist in chamberdict.values():
        # Sort the chambers
        chamberlist = natsorted(chamberlist)

        # Extract chamber numbers from chamberlist
        chambernums = ''.join([chamber[0] for chamber in chamberlist])

        # Make an experiment description filename for chambers in chamberlist
        expdesc = gprdir + '/experiment_description_' + chambernums + '.txt'

        # Do not overwrite expdesc if it already exists
        prevent_overwrite(expdesc)

        # Append this experiment description filename to expdescs
        expdescs.append(expdesc)

        # Open experiment description file for writing
        with open(expdesc, 'w') as f:
            for chamber in chamberlist:
                # Write the header for this chamber
                f.write('Pbm=1\nConcentration=100\nCy3=FOO\n')

                # Find all the filenames for this chamber and write to file
                match = [filename for filename in files if chamber in filename]
                for m in match:
                    f.write(m + '\n')

                # Add an empty line between chambers
                f.write('\n')

    # Return list of experiment description filenames
    return(expdescs)


def make_masliner_comfile(expdesc, comfile):
    """Makes a comfile for running masliner

    Inputs:
        expdesc: the path to the experiment description file to use
        comfile: the path to the comfile to create
    """
    # Do not overwrite comfile if it already exists
    prevent_overwrite(comfile)

    # Open file for writing
    with open(comfile, 'w') as f:
        f.write('perl /project/siggers/perl/GENEPIX/masliner_list.pl\n')
        f.write('-i ' + expdesc) 


def run_masliner_comfile(gprdir, comfile):
    """Runs a comfile for running masliner

    Inputs:
        gprdir: the path to the directory where the gpr files are stored
        comfile: the path to the comfile to run
    """
    # Navigate to gprdir after saving current directory
    cwd = subprocess.os.getcwd()
    subprocess.os.chdir(gprdir)

    # Read contents of comfile as single string on one line
    with open(comfile) as f:
        comfilecont = f.read().replace('\n', ' ')

    # Run comfile
    logging.info('qsub -sync y -P siggers -m a -cwd -N masliner -V -b y ' +
            comfilecont)
    subprocess.run(['qsub', '-sync', 'y', '-P', 'siggers', '-m', 'a', '-cwd',
        '-N', 'masliner', '-V', '-b', 'y', comfilecont])

    # Navigate back to original directory
    subprocess.os.chdir(cwd)


def check_r2(ofile, r2cutoff):
    """Checks masliner output file to make sure R^2 values are above cutoff

    Inputs:
        ofile: the masliner output file to check
        r2cutoff: the R^2 value cutoff
    """
    # Open the file for reading only
    with open(ofile, 'r') as f:
        # Loop through the lines in the file
        for l in f:
            # Find lines containing R^2 values
            if 'R^2=' in l:
                # Extract R^2 value
                start = l.find('=') + 1
                end = l.find(' ', start)
                r2 = float(l[start:end])

                # Abort if R^2 value is less than r2cutoff
                if r2 < r2cutoff:
                    logging.error('R^2 value in ' + ofile + ' is less than '
                            + str(r2cutoff) +
                            '\nPlease select additional gpr files to exclude')
                    raise ValueError('R^2 value in ' + ofile + ' is less than '
                            + str(r2cutoff) +
                            '\nPlease select additional gpr files to exclude')


def masliner_wrapper(gprdir, exclude, maslinerdir, r2cutoff):
    """Runs masliner on all gpr files (except exclude) in a given directory

    Inputs:
        gprdir: the path to the directory where the gpr files are saved
        exclude: the list of gpr files to exclude from analysis
        maslinerdir: the path to the directory in which to save the output files
        r2cutoff: the cutoff for the R^2 values in the masliner output
    """
    # If maslinerdir already exists, abort to prevent overwrite
    prevent_overwrite(maslinerdir)

    # Get a list of all files in gprdir before running masliner
    beforefiles = glob.glob(gprdir + '/*')

    # Change headers of gpr files so 635s and 647s become 488s
    logging.info('Changing 635/647 to 488 in headers for ' +
            'masliner compatibility')
    to_488(gprdir)

    # Make experiment description file(s) in gprdir
    logging.info('Making experiment description file(s)')
    expdescs = make_experiment_description(gprdir, exclude)

    # Make masliner comfile(s) in gprdir
    logging.info('Making masliner comfile(s)')
    # Initialize an array to store the comfile name(s)
    comfiles = []
    for expdesc in expdescs:
        # Extract the file number from the experiment description filename
        start = expdesc.rfind('_') + 1
        end = expdesc.rfind('.')
        filenum = expdesc[start:end]

        # Make a comfile with filenum
        comfile = gprdir + '/masliner_' + filenum + '.com'
        make_masliner_comfile(expdesc, comfile)

        # Append comfile to list of comfiles
        comfiles.append(comfile)

    # Run masliner comfile(s)
    logging.info('Running masliner comfile(s) (this may take a few minutes)')
    for comfile in comfiles:
        run_masliner_comfile(gprdir, comfile)

    # Get a list of all files in gprdir after running masliner
    afterfiles = glob.glob(gprdir + '/*')

    # Get a list of all new files in gprdir
    newfiles = [filename for filename in afterfiles
            if filename not in beforefiles]

    # Make a new directory and move all new files to this directory
    subprocess.run(['mkdir', maslinerdir])
    logging.info('Moving files to masliner directory: ' + maslinerdir)
    for filename in newfiles:
        subprocess.run(['mv', filename, maslinerdir])

    # Check R^2 values in masliner output files
    logging.info('Checking R^2 values in masliner output\n')
    ofiles = glob.glob(maslinerdir + '/masliner.o*')
    for ofile in ofiles:
        check_r2(ofile, r2cutoff)


