from tkinter.messagebox import showinfo

import numpy as np
import pandas as pd
from fitparse import FitFile

def medfilt(x, k):
    """Apply a length-k median filter to a 1D array x.
    Boundaries are extended by repeating endpoints.
    """
    assert k % 2 == 1, "Median filter length must be odd."
    assert x.ndim == 1, "Input must be one-dimensional."
    k2 = (k - 1) // 2
    y = np.zeros((len(x), k), dtype=x.dtype)
    y[:, k2] = x
    for i in range(k2):
        j = k2 - i
        y[j:, i] = x[:-j]
        y[:j, i] = x[0]
        y[:-j, -(i + 1)] = x[j:]
        y[-j:, -(i + 1)] = x[-1]
    return np.median(y, axis=1)


def load_fitfile(filename):
    """

    Parameters
    ----------
    filename

    Returns
    -------

    """

    fit_file = FitFile(filename)

    heartrate = []
    power = []
    time = []
    count = 0
    records = fit_file.get_messages("record")
    timestamp = None
    power = None
    for record in records:
        hr = None
        for data in record:
            """
            altitude: 185.0 [m]
distance: 0.0 [m]
enhanced_altitude: 185.0 [m]
heart_rate: 86 [bpm]
temperature: 20 [C]
timestamp: 2022-09-15 07:47:59
"""
            if data.name == "heart_rate":
                hr = data.value
            if data.name == "timestamp":
                timestamp = data.value
                pass
            if data.name == "power":
                power = data.value

        if hr != None:
            heartrate.append(int(hr))
            #power.append(int(pwr))
            # time.append(datetime.timedelta(seconds=count))
            time.append(count)
            count += 1

    df = pd.DataFrame()
    df['timestamp'] = time
    df['heartrate'] = heartrate
    #df['power'] = power

    i = 0
    # Initialize an list to store moving averages
    window_size = 10
    moving_averages = heartrate[i: window_size - 1]
    while i < len(heartrate) - window_size + 1:
        # Store elements from i to i+window_size
        # in list to get the current window
        window = heartrate[i: i + window_size]

        # Calculate the average of current window
        window_average = round(sum(window) / window_size)
        # window_average = heartrate[i] + 1

        # print("HR {}, Ave HR {}".format(heartrate[i+window_size], window_average))
        # Store the average of current
        # window in moving average list
        moving_averages.append(window_average)

        # Shift window to right by one position
        i += 1

    df['avehr'] = moving_averages

    return df


def load_hrv(filename):
    """

    Parameters
    ----------
    filename

    Returns
    -------

    """
    fit_file = FitFile(filename)
    # 1.5 = 40bpm - min heart rate
    artifacts = 0
    RRs = []
    for record in fit_file.get_messages('hrv'):
        for record_data in record:
            for RR_interval in record_data.value:
                if RR_interval is not None:
                    # todo: set this from configuration
                    # prefilter at max/min HR 40 / 200 bpm
                    if RR_interval < 1.5 and RR_interval > 0.3:
                        print(RR_interval)
                        RRs.append(RR_interval)
                    else:
                        artifacts += 1

    filter = 0.15  # make this user adjustable
    last = None
    artifacts = 0
    heartrate = []
    filtered_RRs = []

    for i in range(len(RRs)):
        if last == None:
            filtered_RRs.append(RRs[i])
            heartrate.append(60 / RRs[i])
            last = RRs[i]
        elif (last * (1 - filter)) <= RRs[i] <= (last * (1 + filter)):
            last = RRs[i]
            filtered_RRs.append(RRs[i])
            heartrate.append(60 / RRs[i])
        else:
            artifacts += 1

    x = np.cumsum(filtered_RRs)
    _start = 0
    _end = len(x)

    showinfo(
        title='HRV Loaded',
        message="Removed {} artifacts out of {} points\nerror rate is {}%".format(artifacts, len(RRs),
                                                                                  artifacts / len(RRs) * 100)
    )

    """
    if _start != 0:
        df = pd.DataFrame()
        df['timestamp'] = x[_start: _end]
        df['RR'] = filtered_RRs[_start: _end]
        df['heartrate'] = heartrate[_start: _end]
    """

    print("Total points {}".format(_end))
    df = pd.DataFrame()
    df['timestamp'] = x  # pd.to_datetime(x, unit='m') # convert to datetimex
    df['RR'] = filtered_RRs
    df['heartrate'] = heartrate

    return df
