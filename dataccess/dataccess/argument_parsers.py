
def addparser_init(subparsers):
    init = subparsers.add_parser('init', help =  'Initialize config.py in local directory.')
    # Unfortunate hack to figure out which subcommand was called. It looks
    # like the dest keyword for add_parser isn't usable in python 2.7.
    init.add_argument('--initcalled', help = 'dummy argument')


def addparser_xes(subparsers):
    # XES analysis sub-command
    xes = subparsers.add_parser('spectrum', help = 'Process area detector data into spectra.')
    xes.add_argument('detid', type = str, help = 'Detector ID.')
    xes.add_argument('labels', nargs = '+', help = 'Labels of datasets to process into spectra.')
    xes.add_argument('--pxwidth', '-p', type = int, default = 3, help = 'Pixel width of CSPAD subregion to sum.')
    xes.add_argument('--rotate', '-r', action = 'store_true', help = "Toggles the area detector's axis of integration for generating spectra")
    xes.add_argument('--calibration', '-c', type = str, help = 'Label of dataset to use for calibration of the energy scale (if --energy_ref1_energy_ref2_calibration is selected but a calibration file is not provided). If not provided this parameter defaults to the first dataset in labels.')
    xes.add_argument('--subtraction', '-d', type = str, help = 'Label of dataset to use as a dark frame subtraction')
    xes.add_argument('--energy_ref1_energy_ref2_calibration', '-k', action = 'store_true', help = 'Enable automatic generation of energy calibration based on k alpha and k beta peak locations if --calibration_load_path is not given.')
    xes.add_argument('--eltname', '-e', default = '', help = 'Element name. This parameter is required for XES-based calibration; i.e., for generating an energy scale using ENERGY_REF1_ENERGY_REF2_CALIBRATION.')
    xes.add_argument('--calibration_save_path', '-s', type = str, help = 'Path to which to save energy calibration data if calibration_load_path is unspecified and --energy_ref1_energy_ref2_calibration is selected.')
    xes.add_argument('--calibration_load_path', '-l', type = str, help = 'Path from which to load energy calibration data.')
    xes.add_argument('--normalization', '-n', action = 'store_true', help = 'If selected, normalization is suppressed')
    xes.add_argument('--nosubtraction', '-ns', action = 'store_true', help = 'If selected, background subtraction is suppressed')
    xes.add_argument('--variation', '-v', action="store_const", default = False, const=True, help ="Plot shot to shot variation")
    xes.add_argument('--variation_n', '-vn', type=int, default = 50, help="How many shots to use for variation")
    xes.add_argument('--variation_center', '-vc', type = int, default = 408, help="to the right is the pump, to the left is the probe")
    xes.add_argument('--variation_skip_width', '-vs', type=int, default=0, help="from vc skip this many inds before summing pump and probe area")
    xes.add_argument('--variation_width', '-vw', type=int, default=50, help="from vc sum out this many inds")


def addparser_xrd(subparsers):
    xrd = subparsers.add_parser('xrd', help = 'Process quad CSPAD data into powder patterns.')
    
    xrd.add_argument('detid', type = str, help = 'Detector ID.')
    xrd.add_argument('labels', nargs = '+', help = 'One or more dataset labels to process.')
    xrd.add_argument('--compounds', '-c', nargs = '+', help = 'Chemical formulas of crystalline species in the sample. If --background_subtraction is passed these MUST be provided.')
    xrd.add_argument('--background_subtraction', '-b', action = 'store_true', help = 'If selected, background subtraction will be performed by interpolation based on the signal between Bragg peaks.')
    xrd.add_argument('--peak_progression_compound', '-p', type = str, help = 'Compound for which to plot the progression of Bragg peak intensities as a function of incident flux if two or more datasets are being processed. If not specified, this option defaults to the first value of COMPOUNDS.')
    xrd.add_argument('--normalization', '-n', type = str, default = None, help = "Normalization option.\n\tIf == 'transmission', normalize by beam transmission specified in logbook;\n\tIf == 'background', normalize by background level (requires --compounds).\nBy default no normalization is applied to powder patterns, and peak progression plots are normalized by background level.")
    xrd.add_argument('--maxpeaks', '-m', type = int, default = None, help = "Limit the plot of peak intensities as a function of incident flux to the MAXPEAKS most intense ones")
    xrd.add_argument('--plot_progression', '-r', action = 'store_true', help = "Plot the progression of Bragg peak intensities as a function of x ray intensity (requires logbook data).")


def addparser_histogram(subparsers):
    import numpy as np
    histogram = subparsers.add_parser('histogram', help =  'For a given dataset and detector ID, evaluate a function (defined in config.py) over all events and plot a histogram of the resulting values.')
    histogram.add_argument('detid', type = str, help = 'Detector ID.')
    histogram.add_argument('labels', nargs = '+', help = 'Labels of one or more datasets to process.')
    histogram.add_argument('--function', '-u', default = None, help = 'Name of function (defined in config.py) to evaluate over all events. Defaults to None.')
    histogram.add_argument('--filter', '-f', action = 'store_true', help = 'If selected, logbook-specified event filtering will be applied.')
    histogram.add_argument('--separate', '-s', action = 'store_true', help = 'If selected, different labels are added separately (with different color).')
    histogram.add_argument('--nbins', '-n', type = int, default = 100, help = 'Number of bins in the histogram.')


def addparser_datashow(subparsers):
    datashow = subparsers.add_parser('datashow', help = 'For a given dataset and area detector ID, show the summed detector image and save it to a file in the working directory. Any detector masks specified in config.py can optionally be applied.')
    datashow.add_argument('detid', type = str, help = 'Detector ID.')
    datashow.add_argument('labels', nargs = '+', help = 'Labels of dataset to process.')
    datashow.add_argument('--output', '-o', help = 'Path of output file')
    datashow.add_argument('--masks', '-m', action = 'store_true',
        help = 'Apply detector masks from config.py')
    datashow.add_argument('--max', '-a', type = int, help = "Maximum amplitude of color scale")
    datashow.add_argument('--min', '-l', type = int, help = "Min amplitude of color scale")
    datashow.add_argument('--run', '-r', type = int, help = 'Individual event number to plot')


def addparser_eventframes(subparsers):
    datashow = subparsers.add_parser('eventframes', help = 'For a given dataset and area detector ID, show the summed detector image and save it to a file in the working directory. Any detector masks specified in config.py can optionally be applied.')
    datashow.add_argument('detid', type = str, help = 'Detector ID.')
    datashow.add_argument('label', help = 'Label of dataset to process.')
    datashow.add_argument('--output', '-o', help = 'Path of output file')
    datashow.add_argument('--masks', '-m', action = 'store_true',
        help = 'Apply detector masks from config.py')
