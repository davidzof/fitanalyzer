from tkinter.messagebox import showinfo

import numpy as np
import pandas as pd
from fitparse import FitFile

class FitParser():

    def load(self, filename, max_hr, min_hr):
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
        cadence = []
        altitude = []
        time = []
        count = 0
        records = fit_file.get_messages("record")
        starttime = None
        delta = None

        hr = 0
        pwr = -1000
        cad = 0
        alt = -1000
        speed = 1
        for record in records:
            ctime = 0
            for data in record:
                # parse a fitfile record

                """
                distance: 0.0 [m]
                cadence ???
    
                temperature: 20 [C]
                timestamp: 2022-09-15 07:47:59
                """

                if data.name == "speed":
                    speed = data.value
                    if data.value == 0 and delta is not None:
                        print(delta.total_seconds())
                if data.name == "heart_rate":
                    hr = data.value
                    if hr < min_hr or hr > (max_hr + 10):
                        break;
                if data.name == "timestamp":
                    ctime = data.value
                if data.name == "power":
                    pwr = data.value

                if data.name == "cadence":
                    cad = data.value

                if data.name == "altitude":
                    alt = data.value

            if speed > 0:
                if starttime == None:
                    starttime = ctime
                delta = ctime - starttime

                # don't record when we are stopped
                heartrate.append(int(hr))
                power.append(int(pwr))
                cadence.append(int(cad))
                altitude.append(int(alt))
                time.append(delta.total_seconds())
            else:
                if delta is not None:
                    starttime = ctime - delta
                else:
                    starttime = ctime

        df = pd.DataFrame()
        df['timestamp'] = time
        df['heartrate'] = heartrate
        df['power'] = power
        df['cadence'] = cadence
        if alt != -1000:
            df['altitude'] = altitude

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
