"""
Module containing default configuration parameter values. These should be
loaded at the top of config.py as follows: "from dataccess.default_config import *"
"""

# redirect stdout to log file
stdout_to_file = False

# Log file location
logfile_path = None

# If False, only print stdout from the rank 0 mode when running with MPI
suppress_root_print = True

plotting_mode = 'console'

# Available batch queues
queues = ('psanaq', 'psfehq', 'psnehq')

import matplotlib.pyplot as plt
