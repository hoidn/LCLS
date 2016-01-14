from collections import namedtuple
import numpy as np

# TODO: figure out a detector ID naming convention based on not-too-verbose
# names from the psana framework

smd = False

# Experiment name specification. Example (from LD67):
exppath = 'mec/mecd6714'
try:
    expname = exppath.split('/')[1]
except:
    raise ValueError("config.exppath: incorrect format")
xtc_prefix = "e441"

# Probe photon energy
photon_energy = 7780.
# Energy per pulse, in J
pulse_energy = 1e-3

# Size in microns of the beam spot at best focus
best_focus_size = 2.

# url of the google doc logbook
url =  "https://docs.google.com/spreadsheets/d/1Ejz-kyf-eoCtI1A76f1qfpS2m6nThosWDrh2dXUjv5g/edit#gid=0&vpid=A1"

# List of detector identifiers
#detID_list = [1, 2, 3]

# Format string for batch job submission
batch_command = "bsub -q psanaq -n 1 -o log.out python %s"



# structure to store area detector information
# TODO: interfacing with Testing.nb.
# Quad CSPAD position parameters in the form of a dictionary of detector IDs
# to parameter dictionaries. Parameter values are obtain by running Alex's
# Mathematica notebook for this.  Coordinates are in pixels; 0.011cm per
# pixel.  See Testing.nb for details.  This information must be provided to
# run XRD analysis.
# Map from detector IDs to a list of 0 or more paths for additional mask files
# (beyond what psana applies to 'calibrated' frames). 
#   -For composite detectors, this program expects masks corresponding to
#   assembeled images.
#   -Multiple masks are ANDed together.
#   -Mask files must be boolean arrays saved in .npy format.
#   -Masks must be positive (i.e., bad/dummy pixels are False).
DetInfo = namedtuple('DetInfo', ['device_name', 'dimensions', 'geometry', 'extra_masks'])

detinfo_map =\
    {'quad':
        DetInfo('MecTargetChamber.0:Cspad.0',
        (830, 825),
        {'phi': 0.027763, 'x0': 322.267, 'y0': 524.473, 'alpha': 0.787745, 'r': 1082.1},
        {'masks/mask_ld67_12_2015.npy'}),
     'xrts1':
        DetInfo('MecTargetChamber.0:Cspad2x2.1',
        (400, 400),
        {},
        {}),
    'xrts2':
        DetInfo('MecTargetChamber.0:Cspad2x2.2', 
        (400, 400),
        {},
        {})}



# Map from detector IDs to a list of 0 or more paths for additional mask files
# (beyond what psana applies to 'calibrated' frames). 
#   -For composite detectors, this program expects masks corresponding to
#   assembeled images.
#   -Multiple masks are ANDed together.
#   -Mask files must be boolean arrays saved in .npy format.
#   -Masks must be positive (i.e., bad/dummy pixels are False).
extra_masks = {
}

# Map from sample composition designator to either (1) a list of powder peak
# angles (units of degrees) or (2) a path to a file containing a simulated
# powder pattern from which peak angles can be extracted. This data is used
# for applying background subtraction in XRD analysis.
powder_angles = {
    'Fe3O4': [31.3, 37.0, 38.8, 45.1, 52.4, 56.0, 59.7, 65.7]
}

# TODO (maybe): parameters for xes analysis script

# port for ZMQ sockets
port = "5560"

def sum_window(smin, smax):
    return lambda arr: smin < np.sum(arr) < smax