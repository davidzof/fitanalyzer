import pandas as pd
from tcxreader.tcxreader import TCXReader, TCXTrackPoint

class TcxParser():
    def load(self, filename, max_hr, min_hr):
        """
        Loads time, heartrate, altitude data from GPX format file using minidom

        Parameters
        ----------
        filename    Name of GPX File to load

        Returns
        -------

        """

        heart_rate = 0
        heartrate = []
        altitude = []
        timestamps = []
        count = 0
        starttime = None
        delta = None


        tcx_reader = TCXReader()
        tcx_exercise = tcx_reader.read(filename)
        for trackpoint in tcx_exercise.trackpoints:
            print(trackpoint)

        df = pd.DataFrame()
        df['timestamp'] = timestamps
        df['heartrate'] = heartrate
        # check altitude is not empty
        df['altitude'] = altitude

        i = 0
        # Initialize  list to store moving averages
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
