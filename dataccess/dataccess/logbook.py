# Author: O. Hoidn

import time
import re
import sys
import json
import webbrowser
import logging
import argparse
import zmq
import hashlib
import ipdb

import httplib2
import os.path


from apiclient import discovery
from oauth2client import client
from oauth2client.file import Storage

import gspread
import pandas as pd
import numpy as np
from atomicfile import AtomicFile

import dill
from dataccess import utils
import config

PORT = config.port

# Format specification for column headers in logbook. Column descriptions:
# runs: range of run numbers in the format 'integer' or 'integer-integer'.
#   Used by: all.
# labels: dataset label, an arbitrary string. This is the only column of which
#   there can be more than one (i.e. a dataset may have more than one label).
#   Used by: all.
# transmission: The fraction of XFEL photons transmitted through upstream filters,
#   in decimal format. Used by: xrd.
# focal_size: focal spot size diameter, in microns. Used by: xrd.
# filter_func: name of a function, defined in config.py, that returns an event-
#   filtering function given 0, 1, or two arguments provided in the param1 and
#   param2 columns. Optional; used by: all.
# param1: first parameter to constructor for event filtering function.
#   Used by: all.
# param2: second parameter to constructor for event filtering function.
#   Used by: all.
# filter_det: detector id of detector whose data is fed to filter_func for
#   event-based filtering. Used by: all
PROPERTY_REGEXES = {'runs': r'.*[rR]un.*', 'transmission': r'.*[tT]ransmission.*',
     'focal_size': r'.*[Ss]ize.*', 'labels': r'.*[lL]abel.*|.*[hH]eader.*',
    'param1': r'.*[pP]aram1.*', 'param2': r'.*[pP]aram2.*',
    'param3': r'.*[pP]aram3.*', 'param4': r'.*[pP]aram4.*',
'filter_det': r'.*[fF]ilter.*[dD]et.*', 'filter_func': r'.*[fF]ilter.*[fF]unc.*'}
HEADERS = [k for k in PROPERTY_REGEXES]

# Format for the flag that designates logbook header row
HEADER_REGEX = r'.*[hH]eader.*'

def get_property_key(col_title):
    for k, v in PROPERTY_REGEXES.iteritems():
        if re.match(v, col_title):
            return k
    raise KeyError(col_title + ": no match found")

# TODO: support the addition of authentication tokens for new users.

def acquire_oauth2_credentials(secrets_file):
    """
    Flows through OAuth 2.0 authorization process for obtaining Google API
    access credentials for a google account's Drive spreadsheets. This requires
    user authentication.

    Parameters:
        secrets_file : str
        secrets file contains this application's client ID and secret
    """
    flow = client.flow_from_clientsecrets(
        secrets_file,
        scope='https://spreadsheets.google.com/feeds',
        redirect_uri='urn:ietf:wg:oauth:2.0:oob')
    
    auth_uri = flow.step1_get_authorize_url()
    webbrowser.open(auth_uri)
    
    auth_code = raw_input('Enter the authentication code: ')
    
    credentials = flow.step2_exchange(auth_code)
    return credentials

# utility functions
def prefix_add(*args):
    return reduce(lambda x, y: x + y, args)

def list_vstack(*args):
    return reduce(prefix_add, args)

def get_cell_coords(sheet_list2d, regex):
    for i, row in enumerate(sheet_list2d):
        for j, cell in enumerate(row):
            if re.search(regex, cell):
                return i, j
    raise ValueError(regex + ": matching cell not found")

@utils.memoize(timeout = 10)
def get_logbook_data(url, sheet_number = 0):
    """
    Given a worksheet URL, return a two-tuple consisting of:
        -A list column names from the sheets, with order and values matching
            the keys of PROPERTY_REGEXES.
        -The spreasheet data as a list, in the corresponding order.
    """
    # TODO: handling (or at least raising an appropriate exception) in the
    # case that the number of label columns is not the same in all sheets.
    storage =  Storage(utils.resource_path('data/credentials'))
    credentials = storage.get()
    gc = gspread.authorize(credentials)
    document = gc.open_by_url(url)
    worksheets = document.worksheets()
    def regex_indexes(regex, col_titles):
        # indices of columns matching the regex
        return [i for i, title in enumerate(col_titles) if re.search(regex, title)]
    def process_one_sheet(sheet):
        """
        given a worksheet, return the data as list with order and contents
        matching the keys of property_regexes.

        Returns None if the sheet doesn't contain at least two rows of values.
        """
        raw_data = sheet.get_all_values()
        try:
            header_i, header_j = get_cell_coords(raw_data, HEADER_REGEX)
        except ValueError:
            header_i = 0
        #ipdb.set_trace()
        if len(np.shape(raw_data)) != 2: # sheet has 0 or 1 filled rows
            print "sheet ", str(sheet), ": no data found"
            return
        col_titles = raw_data[header_i]
        values = raw_data[header_i + 1:]
        num_rows = len(values)
        def get_column_data(regex):
            """
            Given a regex for a column title, return the data.

            Note that the label regex is a special case, since there may be
            more than one matching column. 
            """
            indexes = regex_indexes(regex, col_titles)
            matching_titles = [col_titles[i] for i in indexes]
            if len(indexes) > 1:
                if regex != PROPERTY_REGEXES['labels']:
                    raise ValueError("More than one column matching " + regex + " found.")
                else:
                    return matching_titles, [zip(*values)[i] for i in indexes]
            else:
                if len(indexes) == 0:
                    print regex, ": heading not found"
                    if regex == PROPERTY_REGEXES['labels']:
                        return [None], [[None] * num_rows]
                    else:
                        return [None], [None] * num_rows
                else:
                    return matching_titles, zip(*values)[indexes[0]]
        output = []
        output_col_titles = []
        for k in PROPERTY_REGEXES:
            matching_titles, data = get_column_data(PROPERTY_REGEXES[k])
            output_col_titles += matching_titles
            # 'labels' property can have one or more columns
            if k == 'labels' and len(np.shape(data)) > 1:
                output += data
            else:
                output.append(data)
        #ipdb.set_trace()
        return output_col_titles, zip(*output)
    worksheets_data = []
    for sheet in worksheets:
        sheet_data = process_one_sheet(sheet)
        if sheet_data:
            worksheets_data.append(sheet_data)
    sheets_col_titles, sheets_data = zip(*worksheets_data)
    col_titles = sheets_col_titles[0]
    # TODO: write an appropriate assertion here
    #assert reduce(lambda x, y: x if x == y else 0, col_titles)
    return col_titles, prefix_add(*sheets_data)


def parse_float(flt_str):
    return float(flt_str)

def parse_focal_size(flt_str):
    # TODO: document the allowable notation 
    if 'best focus' in flt_str:
        return config.best_focus_size
    else:
        if 'um' in flt_str:
            flt_str = flt_str.strip('um')
        return parse_float(flt_str)

def parse_string(string):
    return string

def parse_run(run_string):
    """
    Given a string from the "runs" column in the logbook, of the
    format "abcd" or "abcd-efgh", returns a tuple of ints of the format
    (abcd, efgh) denoting start and end numbers of a series of runs.

    Returns ValueError on an incorrectly-formatted string.
    """
    if not run_string:
        return (None, None)
    else:
        split = run_string.split('-')
        try:
            split = map(int, split) # values convertible to ints?
            if len(split) == 1:
                return 2 * tuple(split)
            elif len(split) == 2:
                return tuple(split)
            else:
                raise ValueError("Invalid run range format: ", run_string)
        except:
            raise ValueError("Invalid run range format: ", run_string)

parser_dispatch = {'runs': parse_run, 'transmission': parse_float,
    'param1': parse_float, 'param2': parse_float, 'param3': parse_float,
    'param4': parse_float, 'filter_det': parse_string,
     'labels': parse_string, 'focal_size': parse_focal_size, 'filter_func': parse_string}

def get_label_mapping(url = config.url):
    # TODO: handle duplicates
    if not url:
        raise ValueError("No logbook URL provided")
    label_dict = {}
    col_titles, data = get_logbook_data(url)
    enumerated_titles = list(enumerate(col_titles))
    enumerated_labels = filter(lambda pair: pair[1] and re.search(PROPERTY_REGEXES['labels'], pair[1]), enumerated_titles)
    enumerated_properties = filter(lambda pair: pair[1] and not re.search(PROPERTY_REGEXES['labels'], pair[1]), enumerated_titles)
    for i, row in enumerate(data):
        for j, label in enumerated_labels:
            if label and row[j]:
                local_dict = label_dict.setdefault(row[j], {})
                for k, property in enumerated_properties:
                    property_key = get_property_key(property)
                    if property_key == 'runs':
                        try:
                            local_dict.setdefault(property_key, []).append(parse_run(row[k]))
                            # Delete possible duplicates
                            local_dict[property_key] = list(set(local_dict[property_key]))
                        except ValueError:
                            print "Malformed run range: ", row[k]
                    # TODO: make this non-obvious behaviour clear to the user.
                    elif property and (property not in local_dict) and row[k]:
                        local_dict[property_key] = parser_dispatch[property_key](row[k])
    return label_dict

#def url_list_porthash(url_list):
#    return int(5000 + int(hashlib.sha1(''.join(url_list)).hexdigest(), 16) % 1000)

#def main(url_list = config.url, port = None):
#    #ipdb.set_trace()
#    start = time.time()
#    timeout = 40.
#    if port is None:
#        port = config.port
#        #port = url_list_porthash(url_list)
#    context = zmq.Context()
#    socket = context.socket(zmq.PUB)
#    socket.bind("tcp://*:%s" % port)
#    while time.time() - start < 20:
#        #ipdb.set_trace()
#        logbook_dicts =\
#            [get_label_mapping(url = url)
#            for url in url_list]
#        for map in mapping:
#            print map
#        mapping = utils.merge_dicts(*logbook_dicts)
#        messagedata = dill.dumps(mapping)
#        print mapping
#        topic = config.expname
#        socket.send("%s%s" % (topic, messagedata))
#        time.sleep(1)
#    socket.close()
#    context.term()

def main(url = config.url, port = PORT):
    context = zmq.Context()
    socket = context.socket(zmq.PUB)
    socket.bind("tcp://*:%s" % port)

    while True:
        #topic = 0
        # TODO: topic shouldn't be null
        mapping = get_label_mapping(url = url)
        messagedata = dill.dumps(mapping)
        print mapping
        topic = config.expname
        socket.send("%s%s" % (topic, messagedata))
        time.sleep(1)
