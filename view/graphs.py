from typing import Union, List

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

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

    # Zones
    plt.hlines(162, 0, last, color='red', linestyle='dashed', label='LT2')
    plt.hlines(148, 0, last, color='green', linestyle='dashed', label='LT1')
    plt.legend(loc='upper right')
    plt.grid()
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


def plot_zones(df):
    """

    Parameters
    ----------
    df - data fields to be plotted

    Returns
    -------

    """
    zones = [148, 162]  # three zones < 148, 148-162 and > 162

    avehr = df['avehr']
    last_zone = 0
    start = 0
    i = 0
    zz = []
    tstamp = []
    annotations = []
    while i < len(avehr):
        hr = avehr[i]
        ts = df['timestamp'][i]
        zone = 1
        for zone_hr in zones:
            if hr < zone_hr:
                break
            zone += 1

        if zone != last_zone:
            # change in zone
            if ts != 0:
                # not the initial change, record the end of the last zone
                zz.append(last_zone)
                tstamp.append(ts - 1)
                print("zone {} ts {}".format(last_zone, ts - 1))
                if last_zone > 1:
                    zlen = ts - start

                    if zlen >= 120:
                        print("zone {}, zone length = {}".format(last_zone, zlen))
                        m, s = divmod(zlen, 60)
                        t = '{:d}:{:02d}'.format(int(m),int(s))
                        annotations.append((ts-(zlen/2), t, last_zone))
                start = ts

            zz.append(zone)
            tstamp.append(ts)

            last_zone = zone
            print("zone {} ts {}".format(zone, ts))

        i = i + 1

    # https://stackoverflow.com/questions/69100231/matplotlib-fill-area-with-different-colors-based-on-a-value
    f, ax = plt.subplots(1)
    z2 = [2] * len(tstamp)
    z1 = [1] * len(tstamp)
    ax.plot(tstamp, zz, color='none')
    polygon = plt.fill_between(tstamp, zz, color='red', alpha=0.3)
    line = np.array(zz)
    zz2 = np.array(z2)
    zz1 = np.array(z1)
    ax.fill_between(tstamp, zz, where=line > zz1,
                    facecolor='red', alpha=0.5, interpolate=True)
    ax.fill_between(tstamp, zz, where=line > zz2,
                    facecolor='red', alpha=0.7, interpolate=True)

    ax.set_ylim(bottom=0)
    plt.legend()
    plt.xlabel('Time')
    plt.ylabel('Zones')
    plt.title('HR Zones')

    for annotate in annotations:
        print(annotate)
        ax.annotate(str(annotate[1]) + "s",
                    xy=(annotate[0], annotate[2]), xycoords='data', fontsize=10, horizontalalignment='center')

    ax.xaxis.set_major_formatter(format_func)
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
