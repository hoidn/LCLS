from dataccess import xrd
from dataccess import query
from dataccess import utils

def make_event_mask(runs, events_included, max_events = 1000):
    """
    Given a list of run numbers, and a list of list of event numbers to be included for each
    run, return an event mask.
    """
    mask = {}
    for r, events in zip(runs, events_included):
        mask[r] = {}
        for i in range(max_events):
            if i in events:
                mask[r][i] = True
            else:
                mask[r][i] = False
    return mask

def make_pattern_getter(detid, peakfinder = False, compound_list = None):
    def pattern_getter(arr, **kwargs):
        return xrd.Pattern.from_dataset(arr, detid, compound_list)
    def pattern_getter_peakfitting(arr, **kwargs):
        from dataccess.peakfinder import peakfilter_frame
        return xrd.Pattern.from_dataset(peakfilter_frame(arr, detid = detid), detid, compound_list)
    if peakfinder:
        return pattern_getter_peakfitting
    return pattern_getter
    
def plot_patterns(patterns, labels= None, show = True):
    if labels is None:
        labels =  [''] * len(patterns)
    ax = None
    for pat, label in zip(patterns[:-1], labels[:-1]):
        ax, _ = pat.plot(ax = ax, show = False, label = label)
    ax, _ = patterns[-1].plot(ax = ax, show = show, label = labels[-1])

def plot_run_events(detid, runs, events, plot_mean = False, plot_individual  = True,
        show = True, peakfinder = False, compound_list = None):
    ds = query.DataSet(runs, label = str(runs) + str(events))
    event_mask = make_event_mask(runs, events)
    pattern_getter = make_pattern_getter(detid, peakfinder = peakfinder, compound_list = compound_list)
    if plot_individual:
        evaluated = ds.evaluate(detid, event_data_getter = pattern_getter,
                                    event_mask = event_mask)
    else:
        evaluated = ds.evaluate(detid, event_mask = event_mask)
    ax = None
    output = []
    if plot_mean:
        pat = xrd.Pattern.from_dataset(evaluated.mean, detid, compound_list)
        output.append(pat)
        if not plot_individual:
            ax, _ = pat.plot(ax = ax, show = show, label = 'runs %s: mean' % str(runs))
        else:
            ax, _ = pat.plot(ax = ax, show = False, label = 'runs %s: mean' % str(runs))

    if plot_individual:
        for r, events in zip(runs, events):
            for event in events:
                pat = evaluated.event_data[r][event]
                output.append(pat)
                if event == events[-1] and r == runs[-1]:
                    ax, _ = pat.plot(ax = ax, show = show, label = 'run %s, event %s' % (r, event))
                else:
                    ax, _ = pat.plot(ax = ax, show = False, label = 'run %s, event %s' % (r, event))
    return output
