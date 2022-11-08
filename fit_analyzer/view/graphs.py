from typing import Union, List

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from fit_analyzer.model.config import Configuration

configuration = Configuration()

"""
Charts to do:
1. HR + Ave HR with Zones
2. Training Zones - calc zones on 15 second contiguous blocks < 15 seconds and it doesn't count.
3. DFA Alpha 1
3. HR DFA Alpha 1 Trendline
5. HR / Power
"""


def onselect(xmin, xmax):
    """
    x is timestamps
    Parameters
    ----------
    xmin
    xmax

    Returns
    -------

    """
    global _start
    global _end
    indmin, indmax = np.searchsorted(x, (xmin, xmax))
    indmax = min(len(x) - 1, indmax)

    # thisx = x[indmin:indmax]
    # thisy = y[indmin:indmax]
    _start = indmin
    _end = indmax


def format_func(x, pos):
    hours = int(x // 3600)
    minutes = int((x % 3600) // 60)
    seconds = int(x % 60)

    return "{:d}:{:02d}:{:02d}".format(hours, minutes, seconds)


def plot_hr(df):
    """

    Parameters
    ----------
    df - data fields to be plotted

    Returns
    -------

    """
    last = df['timestamp'].iat[-1]
    fig, ax = plt.subplots()

    fig.suptitle('Heart Rate\n\n', fontweight="bold")
    # first line
    ax.plot(df['timestamp'], df['heartrate'])
    ax.xaxis.set_major_formatter(format_func)
    fig.autofmt_xdate(rotation=45)

    ax.set_ylabel("Heartrate")
    ax.set_xlabel("Time")
    ax.plot(df['timestamp'], df['avehr'], color="orange", dashes=[1, 0, 1])
    ax.legend()

    # Zones Gridlines
    zones = configuration.getZones()
    for zone in zones:
        if zone[0] is not None:
            plt.hlines(zone[0], 0, last, color=zone[2], linestyle='dashed', label=zone[1])
    plt.legend(loc='upper right')
    plt.grid()
    plt.tight_layout()
    plt.show()


def plot_hrpwr(df):
    fig = plt.figure()

    ax = fig.add_subplot(111)
    ax.plot(df['timestamp'], df['heartrate'])
    ax.xaxis.set_major_formatter(format_func)
    fig.autofmt_xdate(rotation=45)
    lines, labels = ax.get_legend_handles_labels()

    fig.get_axes()[0].set_ylabel("Heartrate")
    fig.get_axes()[0].set_xlabel("Time")

    fig.suptitle('Heart Rate and Power\n\n', fontweight="bold")

    # Display the Power graph
    ax_new = ax.twinx()
    ax_new.spines["right"].set_position(("axes", 1 + 0.1 * (len(df) - 1)))
    ax_new.plot(df['timestamp'], df['power'], color="red")
    ax_new.set_ylabel("Power (Watts)")

    plt.grid()
    plt.show()


def tiz_sg(zone_values, zone_time_stamps):
    """
    Time in Zone / Session Goal model removes time spent in zones that were not relevant to the goal of teh session
    Parameters
    ----------
    zone_values
    zone_time_stamps

    Returns
    -------

    """
    for i in range(0, len(zone_values), 2):
        if i > 0 and (i + 3) < len(zone_values):
            # second zone
            zlen = zone_time_stamps[i + 1] - zone_time_stamps[i]
            zone = zone_values[i]

            next_zone = zone_values[i + 2]
            next_zlen = zone_time_stamps[i + 3] - zone_time_stamps[i + 2]

            last_zone = zone_values[i - 1]
            last_zlen = zone_time_stamps[i + 1] - zone_time_stamps[i - 2]

            if zlen < 120:
                """
                What are the cases?
                1. prev and next are > 120 and prev and next < zone and prev = next,
                consolidate all three zones
                2. prev and next are > 120 and next > zone and prev < zone
                consolidate with next zone
                3. prev and next are > 120 and next < zone and prev > zone
                consolidate with previous

                """
                # print("zone {},{},{}, zone len {}".format(last_zone, zone, next_zone, zlen))

                if last_zlen >= 120 and last_zone == next_zone and zone > 1:
                    # 1 - remove short peaks and troughs
                    zone_time_stamps[i + 2] = zone_time_stamps[i - 2]
                    del zone_values[i + 1]
                    del zone_values[i]
                    del zone_values[i - 1]
                    del zone_values[i - 2]
                    del zone_time_stamps[i + 1]
                    del zone_time_stamps[i]
                    del zone_time_stamps[i - 1]
                    del zone_time_stamps[i - 2]


                elif next_zlen >= 120 and next_zone > zone and zone != 1:
                    zone_time_stamps[i + 2] = zone_time_stamps[i]
                    del zone_values[i + 1]
                    del zone_values[i]
                    del zone_time_stamps[i + 1]
                    del zone_time_stamps[i]

                    """
                    elif next_zlen < 120 and next_zone < zone:
                            zone_time_stamps[i + 1] = zone_time_stamps[i+3]
                            del zone_values[i + 3]
                            del zone_values[i + 2]
                            del zone_time_stamps[i + 3]
                            del zone_time_stamps[i + 2]
                    """
                else:
                    continue
                return tiz_sg(zone_values, zone_time_stamps)

    return zone_values, zone_time_stamps


def annotate(zone_values, zone_time_stamps):
    ### Annotate zones longer than 2 minutes
    annotations = []
    last_ts = 0
    for i in range(len(zone_values)):
        zlen = zone_time_stamps[i] - last_ts
        if zlen >= 120:
            m, s = divmod(zlen, 60)
            t = '{:d}:{:02d}'.format(int(m), int(s))
            annotations.append((zone_time_stamps[i] - (zlen / 2), t, zone_values[i]))

        last_ts = zone_time_stamps[i]

    return annotations


def plot_zones(df, sg_tiz=False):
    """
    Draws a graph of time spent in zones against elapsed time. Gives a vision of intervals and zones. Note only
    zones longer than 2 minutes (120s) get annotated with a timestamp

    Parameters
    ----------
    df - data fields to be plotted
    sgtiz - if true we calculate zones using session goal/time in zone model.

    Returns
    -------

    """
    zones = configuration.getZones()

    avehr = df['avehr']
    last_zone = 0
    start = 0
    i = 0
    zone_values = []
    zone_time_stamps = []
    while i < len(avehr):
        # Loop over all rolling average heart rate entries
        hr = avehr[i]
        ts = df['timestamp'][i]
        current_zone = 1
        for zone in zones:
            # calculate the current_zone based on the heart rate
            if zone[0] is None or hr < zone[0]:
                break
            current_zone += 1

        if current_zone != last_zone:
            # the zone has changed
            if ts != 0:
                # This is not the very first change. Save the last zone end time
                zone_values.append(int(last_zone))
                zone_time_stamps.append(ts)

            zone_values.append(int(current_zone))
            zone_time_stamps.append(ts)

            last_zone = current_zone

        i = i + 1

    if sg_tiz == True:
        ### suppress short zones here for sg/tiz model
        zone_values, zone_time_stamps = tiz_sg(zone_values, zone_time_stamps)

    ### Annotate zones longer than 2 minutes
    annotations = annotate(zone_values, zone_time_stamps)

    """
      Plot zone values with different shadings for each zone
      see: https://stackoverflow.com/questions/69100231/matplotlib-fill-area-with-different-colors-based-on-a-value
    """
    # plot the altitudes, if present
    if 'altitude' in df:
        f, axs = plt.subplots(2)
        axs[0].plot(df['timestamp'], df['altitude'], color='grey')
        axs[0].set_title('Altitude')
        axs[0].grid()
        zone_ax = axs[1]
    else:
        f, zone_ax = plt.subplots(1)

    # plot the background zone chart
    zone_ax.plot(zone_time_stamps, zone_values, color='none')
    plt.fill_between(zone_time_stamps, zone_values, color='red', alpha=(1 / len(zones)))
    line = np.array(zone_values)

    ### TODO fix this we just need to loop over zones len, not zones
    zone_count = 1
    for zone in zones:
        """
        For each zone create an np_array filled with the zone value equal to the length of the graph then plot it
        with darker shading
        """
        zone_graph = [zone_count] * len(zone_time_stamps)
        zone_graph_np = np.array(zone_graph)
        alpha = ((zone_count) / len(zones))
        zone_ax.fill_between(zone_time_stamps, zone_values, where=line > zone_graph_np,
                             facecolor='red', alpha=((zone_count) / len(zones)), interpolate=True)
        zone_count = zone_count + 1

    zone_ax.set_ylim(bottom=0)
    plt.legend()
    plt.xlabel('Time')
    plt.ylabel('Zones')
    plt.title('HR Zones')

    for annotation in annotations:
        print(annotation)
        zone_ax.annotate(str(annotation[1]),
                         xy=(annotation[0], annotation[2]), xycoords='data', fontsize=8, horizontalalignment='center')

    zone_ax.xaxis.set_major_formatter(format_func)
    f.autofmt_xdate(rotation=45)

    plt.tight_layout()
    plt.show()


def plot_multi(
        data: pd.DataFrame,
        x: Union[str, None] = None,
        y: Union[List[str], None] = None,
        spacing: float = 0.1,
        **kwargs
) -> matplotlib.axes.Axes:
    """Plot multiple Y axes on the same chart with same x axis.

    Args:
        data: dataframe which contains x and y columns
        x: column to use as x axis. If None, use index.
        y: list of columns to use as Y axes. If None, all columns are used
            except x column.
        spacing: spacing between the plots
        **kwargs: keyword arguments to pass to data.plot()

    Returns:
        a matplotlib.axes.Axes object returned from data.plot()

    Example:
    >>> plot_multi(df, figsize=(22, 10))
    >>> plot_multi(df, x='time', figsize=(22, 10))
    >>> plot_multi(df, y='price qty value'.split(), figsize=(22, 10))
        start = 0
    end = 10000>>> plot_multi(df, x='time', y='price qty value'.split(), figsize=(22, 10))
    >>> plot_multi(df[['time price qty'.split()]], x='time', figsize=(22, 10))

    See Also:
        This code is mentioned in https://stackoverflow.com/q/11640243/2593810
    """
    from pandas.plotting._matplotlib.style import get_standard_colors

    # Get default color style from pandas - can be changed to any other color list
    if y is None:
        y = data.columns

    # remove x_col from y_cols
    if x:
        y = [col for col in y if col != x]

    if len(y) == 0:
        return
    colors = get_standard_colors(num_colors=len(y))

    if "legend" not in kwargs:
        kwargs["legend"] = False  # prevent multiple legends

    # First axis
    ax = data.plot(x=x, y=y[0], color=colors[0], **kwargs)
    ax.set_ylabel(ylabel=y[0])
    lines, labels = ax.get_legend_handles_labels()

    for i in range(1, len(y)):
        # Multiple y-axes
        ax_new = ax.twinx()
        ax_new.spines["right"].set_position(("axes", 1 + spacing * (i - 1)))
        data.plot(
            ax=ax_new, x=x, y=y[i], color=colors[i % len(colors)], **kwargs
        )
        ax_new.set_ylabel(ylabel=y[i])

        # Proper legend position
        line, label = ax_new.get_legend_handles_labels()
        lines += line
        labels += label

    ax.legend(lines, labels, loc=0)
    return ax
