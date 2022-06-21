import pandas as pd
from platform import system
from matplotlib.widgets import Cursor

pd.core.common.is_list_like = pd.api.types.is_list_like
import pandas_datareader.data as web
import numpy as np
from matplotlib.dates import date2num, DayLocator, DateFormatter
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import seaborn as sns
import datetime
import time
import os.path
from os import path
import yfinance as yahoo_finance

yahoo_finance.pdr_override()
from mplfinance.original_flavor import candlestick2_ohlc
from argparse import ArgumentParser

import imgcompare
from imgcompare import is_equal
import os
from PIL import Image

MAGIC_NUMBER = 50

def get_data(args):
    ticker_df = web.get_data_yahoo(
        args.ticker, period=args.period, interval=args.interval
    )
    if args.start_date:
        ticker_df = ticker_df[args.start_date :]
    if args.stop_date:
        ticker_df = ticker_df[: args.stop_date]
    return ticker_df.reset_index()

def measure_error(x,y):
    return imgcompare.image_diff_percent(x, y)

def log(*argv, **kwargs):
    # if args.verbose:
    print(*argv, **kwargs)

def generate_lines(args, ax, dfRes):
    lines = []
    removed_indexes = []
    x_max = 0
    for index, row in dfRes.iterrows():
        # if index < MAGIC_NUMBER: continue
        if not (index in removed_indexes):
            dropindexes = []
            dropindexes.append(index)
            counter = 0
            values = []
            values.append(row.Value)
            startx = index
            endx = index
            dir = row.Dir
            for index2, row2 in dfRes.iterrows():
                if not (index2 in removed_indexes):
                    if (
                        index != index2
                        and abs(index2 - index) < args.time
                        and row2.Dir == dir
                    ):
                        if abs((row.Value / row2.Value) - 1) < (
                            args.dif / 100
                        ):
                            dropindexes.append(index2)
                            values.append(row2.Value)
                            if index2 < startx:
                                startx = index2
                            elif index2 > endx:
                                endx = index2
                            counter = counter + 1
            if counter + 1 >= args.number:
                sum = 0
                log("Support at ", end="")
                for i in range(len(values) - 1):
                    log("{:0.2f} and ".format(values[i]), end="")
                log("{:0.2f} \n".format(values[len(values) - 1]), end="")
                removed_indexes.extend(dropindexes)
                for value in values: sum = sum + value
                if endx > x_max: x_max = endx
                lines.append([startx, endx, sum / len(values)])
    return lines

def draw_boxes(args, ax, lines):
    from matplotlib.patches import Rectangle
    counter = 0

    def find_overlapping(lines, line):
        ol = []
        for line2 in lines:
            if line2[0] == line[0] and line2[2] == line[2]: continue
            if line[0] < line2[1] and line[1] > line2[0]: ol.append(line2)
        return ol

    def find_min_x(lines, line):
        ol = find_overlapping(lines, line)
        minx = ol[0][0]
        for line2 in ol:
            if line2[0] < minx: minx = line2[0]
        return minx

    def find_max_x(lines, line):
        ol = find_overlapping(lines, line)
        maxx = ol[0][1]
        for line2 in ol:
            if line2[1] > maxx: maxx = line2[1]
        return maxx

    for line in lines:
        for line2 in lines:
            if line2[0] == line[0] and line2[2] == line[2]: continue
            # show all lines where the startx is before this lines' stopx
            if line[1] > line2[0] and line[0] < line2[1]:
                min_x = find_min_x(lines, line)
                max_x = find_max_x(lines, line)
                min_y = min(line[2], line2[2])
                max_y = max(line[2], line2[2])
                # import pdbr; pdbr.set_trace()
                if (max_y - min_y) > 2:
                    ax.add_patch(
                        Rectangle(
                          (min_x, min_y), max_x-min_x, max_y-min_y,
                          facecolor = 'white',
                          edgecolor= 'white',
                          fill=(not args.empty_boxes),)
                    )
    return ax

def createZigZagPoints(dfSeries, minRetrace):
    curVal = dfSeries[0]
    curPos = dfSeries.index[0]
    curDir = 1
    dfRes = pd.DataFrame(index=dfSeries.index, columns=["Dir", "Value"])
    for ln in dfSeries.index:
        if (dfSeries[ln] - curVal) * curDir >= 0:
            curVal = dfSeries[ln]
            curPos = ln
        else:
            retracePrc = abs((dfSeries[ln] - curVal) / curVal * 100)
            if retracePrc >= (minRetrace[ln]):
                dfRes.loc[curPos, "Value"] = curVal
                dfRes.loc[curPos, "Dir"] = curDir
                curVal = dfSeries[ln]
                curPos = ln
                curDir = -1 * curDir
    dfRes[["Value"]] = dfRes[["Value"]].astype(float)
    return dfRes

def prepare_df(df, args):
    df['Range'] = df.High - df.Low
    df['RollingMax'] = df.High.rolling(MAGIC_NUMBER).max()
    df['RollingMin'] = df.Low.rolling(MAGIC_NUMBER).min()
    df['RollingRangeDivClose'] = ((df.RollingMax - df.RollingMin) / df.Close)
    df['MinRetracement'] = df.RollingRangeDivClose * args.retracement_size
    df['MaxDiff'] = df.RollingRangeDivClose * args.dif
    return df

def draw_lines(ax, lines):
    for line in lines:
        ax.hlines(
            y=line[2],
            xmin=line[0],
            xmax=line[1],
            linewidth=1,
            color="w",
        )

def draw_chart(ticker_df, args, lines=None):
    # df['AvgRng'] = df.Range.rolling(MAGIC_NUMBER).mean()
    # axs[1].plot(ticker_df.MinRetracement)
    # axs[1].plot(ticker_df.Range)
    # ax.plot(dfRes["Value"])
    # axs[2].plot(ticker_df.MaxDiff[ticker])
    # ax.text(.5,.8,f'{ticker} magic:{MAGIC_NUMBER}\nRollingRangeDivClose\nMinRetracement\nMaxDiff', horizontalalignment='center', transform=ax.transAxes)

    log("\n\n" + args.ticker)
    df = prepare_df(ticker_df, args)
    fig, axs = plt.subplots(
        1,
        facecolor=(0,0,0),
        sharex=True,
        sharey=False,
        figsize=(15, 8),)
        # gridspec_kw={"height_ratios": [5, 1]},
        # )
    ax = axs
    ax.set_facecolor('black')
    ax.yaxis.set_label_position("right")
    ax.yaxis.tick_right()
    fig.tight_layout()
    fig.subplots_adjust(wspace=0, hspace=0)
    ax.set_ylim([df.Low.min()*0.95, df.High.max()*1.05])
    ax.set_xlim([MAGIC_NUMBER,df.index.max()])
    cursor = Cursor(ax, color="gray", linewidth=1)

    if lines:
        outfile = f"data/samples/{args.ticker}.png"
    else:
        title = f"{args.ticker}/-d {args.dif} -r {args.retracement_size}"
        outfile = f"out/{title}.png"
        if not os.path.exists(os.path.dirname(outfile)):
            os.makedirs(os.path.dirname(outfile))

    dfRes = createZigZagPoints(df.Close, df.MinRetracement).dropna()
    if not args.no_candles:
        print("drawing candles")
        candlestick2_ohlc(ax, df["Open"], df["High"], df["Low"], df["Close"], width=0.5, colorup="g", colordown="r",)

    if not args.no_sr_lines and not lines:
        lines = generate_lines(args, ax, dfRes)

    # draw lines
    draw_lines(ax, lines)
    # if not args.draw_boxes:

    log(lines)

    if lines and args.draw_boxes:
        # print(lines)
        draw_boxes(args, ax, lines)

    # plt.xticks(df.index, labels=df.Date.astype(str))
    # ax.set_xticklabels(labels)
    # plt.xticks(df.index,df.Date)

    # import pdbr; pdbr.set_trace()
    # plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d/%Y'))
    # plt.gca().xaxis.set_major_locator(mdates.DayLocator())
    # plt.axis('off')
    # plt.xticks(np.arange(300), ['Tom', 'Dick', 'Sue']*100)
    # ax.set_xticks(df.index, df.Date)

    import matplotlib.ticker as ti
    def mydate(x,pos):
        try:
            return df.Date.loc[int(x)]
        except :
            return ''
    ax.xaxis.set_major_formatter(ti.FuncFormatter(mydate))

    if args.optimize:
        # print(outfile)
        plt.savefig(outfile)
    else:
        # plt.title(ticker)
        plt.show()

    plt.clf()
    plt.cla()
    plt.close()
    return outfile
