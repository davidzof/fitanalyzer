import math

import numpy as np
import pandas as pd
from tkinter import *
from tkinter.ttk import Progressbar
from fit_analyzer.model import analysis


def DFA1(pp_values, lower_scale_limit, upper_scale_limit):
    """
    Martin Sikora

    Parameters
    ----------
    pp_values
    lower_scale_limit
    upper_scale_limit

    Returns
    -------

    """


    scaleDensity = 30  # scales DFA is conducted between lower_scale_limit and upper_scale_limit
    m = 1  # order of polynomial fit (linear = 1, quadratic m = 2, cubic m = 3, etc...)

    # initialize, we use logarithmic scales
    scales = np.floor(np.logspace(np.log10(lower_scale_limit), np.log10(upper_scale_limit), scaleDensity)).astype('i4')
    F = np.zeros(len(scales))
    # Step 1: Determine the "profile" (integrated signal with subtracted offset)
    y_n = np.cumsum(pp_values - np.mean(pp_values))

    for i, s in enumerate(scales):
        # Step 2: Divide the profile into N non-overlapping segments of equal length s
        n0 = len(pp_values) // s
        shape = (n0, s)
        # beginning to end, here we reshape so that we have a number of segments based on the scale used at this cycle
        Y_n1 = np.reshape(y_n[:n0 * s], shape)
        # end to beginning
        Y_n2 = np.reshape(y_n[-n0 * s:], shape)
        # concatenate
        Y_n = np.vstack((Y_n1, Y_n2)).T

        # Step 3: Calculate the local trend for each 2Ns segments by a least squares fit of the series
        xcut = np.arange(0, s)
        x = np.vstack(tuple([np.ones_like(xcut), ] + [np.power(xcut, i) for i in range(1, m + 1)]))
        beta = np.linalg.solve(x.dot(x.T), x.dot(Y_n))
        arr = x.T.dot(beta) - Y_n
        smse = np.sum(arr * arr)
        F[i] = np.sqrt(smse / (n0 * s * 2))

    x = np.vstack(tuple([np.ones_like(scales), np.log2(scales)]))
    alpha = np.linalg.solve(x.dot(x.T), x.dot(np.log2(F)))[1]
    return alpha


def DFA(pp_values, lower_scale_limit, upper_scale_limit):
    """
    see also pyhrf
    Computing Detrended Fluctuation Analysis (DFA) and alpha 1
    Credit for this code goes to [Sarah Pickus](https://github.com/pickus91/HRV)
    This code is much slower than method above
    """
    scaleDensity = 30  # scales DFA is conducted between lower_scale_limit and upper_scale_limit
    m = 1  # order of polynomial fit (linear = 1, quadratic m = 2, cubic m = 3, etc...)

    # initialize, we use logarithmic scales
    start = np.log(lower_scale_limit) / np.log(10)
    stop = np.log(upper_scale_limit) / np.log(10)
    scales = np.floor(np.logspace(np.log10(math.pow(10, start)), np.log10(math.pow(10, stop)), scaleDensity))
    F = np.zeros(len(scales))
    count = 0

    for s in scales:
        rms = []
        # Step 1: Determine the "profile" (integrated signal with subtracted offset)
        x = pp_values
        y_n = np.cumsum(x - np.mean(x))
        # Step 2: Divide the profile into N non-overlapping segments of equal length s
        L = len(x)
        shape = [int(s), int(np.floor(L / s))]
        nwSize = int(shape[0]) * int(shape[1])
        # beginning to end, here we reshape so that we have a number of segments based on the scale used at this cycle
        Y_n1 = np.reshape(y_n[0:nwSize], shape, order="F")
        Y_n1 = Y_n1.T
        # end to beginning
        Y_n2 = np.reshape(y_n[len(y_n) - (nwSize):len(y_n)], shape, order="F")
        Y_n2 = Y_n2.T
        # concatenate
        Y_n = np.vstack((Y_n1, Y_n2))

        # Step 3: Calculate the local trend for each 2Ns segments by a least squares fit of the series
        for cut in np.arange(0, 2 * shape[1]):
            xcut = np.arange(0, shape[0])
            pl = np.polyfit(xcut, Y_n[cut, :], m)
            Yfit = np.polyval(pl, xcut)
            arr = Yfit - Y_n[cut, :]
            rms.append(np.sqrt(np.mean(arr * arr)))

        if (len(rms) > 0):
            F[count] = np.power((1 / (shape[1] * 2)) * np.sum(np.power(rms, 2)), 1 / 2)
        count = count + 1
    pl2 = np.polyfit(np.log2(scales), np.log2(F), 1)
    alpha = pl2[0]
    return alpha


def computeFeatures(df, start, master):
    """
    Maybe compute DFA for 120 second chunks but for each datapoint
    """
    features = []
    step = 120
    starttime = df['timestamp'][0] + step

    inc = round(len(df['timestamp']) / 100)

    label = Label(master, text='Working...')
    label.pack()
    p = Progressbar(master, orient=HORIZONTAL, length=200, mode="determinate", takefocus=True, maximum=100)
    p.pack()

    cc = 0
    for index in range(0, len(df['timestamp']), 1):
        rmssd = None
        sdnn = None
        alpha1 = None
        alpha2 = None

        if df['timestamp'][index] >= starttime and index % 1 == 0:
            if index % inc == 0:
                # only increments to 97 ??? is it a rounding issue.
                cc += 1
                print(cc)
                # progress bar
                p.step()
                master.update()

            current_time = df['timestamp'][index]
            array_rr = df.loc[
                               (df['timestamp'] >= (current_time - step)) & (df['timestamp'] <= current_time), 'RR'] * 1000
            # compute heart rate
            # heartrate = round(60000/np.mean(array_rr), 2)
            # compute rmssd
            NNdiff = np.abs(np.diff(array_rr))
            rmssd = round(np.sqrt(np.sum((NNdiff * NNdiff) / len(NNdiff))), 2)
            # compute sdnn
            sdnn = round(np.std(array_rr), 2)
            # dfa, alpha 1
            alpha1 = DFA1(array_rr.to_list(), 4, 16)

        heartrate = df['heartrate'][index]

        curr_features = {
            'timestamp': df['timestamp'][index],
            'heartrate': heartrate,
            'rmssd': rmssd,
            'sdnn': sdnn,
            'alpha1': alpha1,
            'alpha2': alpha2,
        }

        features.append(curr_features)

    p.destroy()
    label.destroy()
    features_df = pd.DataFrame(features)
    return features_df
