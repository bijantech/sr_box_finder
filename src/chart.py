import matplotlib.pyplot as plt
import imgcompare
from matplotlib.dates import date2num, DayLocator, DateFormatter
from matplotlib.widgets import Cursor
import matplotlib.dates as mdates
import seaborn as sns
import numpy as np
import time
import os.path
import matplotlib.ticker as ti
from os import path
from matplotlib.patches import Rectangle
from PIL import Image
from mplfinance.original_flavor import candlestick2_ohlc
import pandas as pd
import random
from mathutil import overlap

from utils import log, Box

colors_ = lambda n: list(map(lambda i: "#" + "%06x" % random.randint(0, 0xFFFFFF),range(n)))
MAGIC_NUMBER = 50

class Chart():
    def __init__(self, ticker_df, args, sample=False):
        self.sample = None
        self.covered = None
        self.ticker_df = ticker_df
        self.args = args
        self.is_sample = sample
        self.set_sample()
        self.error = None
        self.draw_chart()
        self.score()
        self.ticker = args.ticker

    def __repr__(self):
        return f"""
            ticker:{self.ticker} error:{self.error} covered:{self.covered}
            outfile:{self.outfile} last_price:{round(self.last_price, 2)} inbox:{self.price_in_box}
            dif:{self.args.dif} ret:{self.args.retracement_size} num:{self.args.number}
            candles:{self.args.show_candles} zags:{self.args.show_zags}
            is_sample:{self.is_sample} sample:{self.sample}
            """
    def set_sample(self):
        if not self.is_sample:
            outfile = f"out/samples/{self.args.ticker}.png"
            if os.path.exists(outfile):
                self.sample = outfile

    def score(self):
        if self.sample:
            sampleimg = Image.open(self.sample).convert('RGB')
            new = Image.open(self.outfile).convert('RGB')
            if sampleimg:
                self.error = measure_error(sampleimg, new)

    def draw_chart(self):
        args = self.args
        ticker_df = self.ticker_df
        log("\n\n" + args.ticker)
        df = prepare_df(ticker_df, args)

        if self.args.side_by_side:
            fig, axs = plt.subplots(
                1, 2,
                facecolor=(0,0,0),
                sharex=True,
                sharey=False,
                figsize=(15, 8),
                num=self.args.ticker,)
                # gridspec_kw={"height_ratios": [5, 1]},
                # )
        else:
            fig, axs = plt.subplots(
                1, #2,
                facecolor=(0,0,0),
                sharex=True,
                sharey=False,
                figsize=(15, 8),
                num=args.ticker,)
                # gridspec_kw={"height_ratios": [5, 1]},
                # )

        try:
            iter(axs)
        except:
            axs = [axs]

        for a in axs:
            a.set_title(args.ticker)
            a.set_facecolor('black')
            a.yaxis.set_label_position("right")
            a.yaxis.tick_right()

        fig.tight_layout()
        fig.subplots_adjust(wspace=0, hspace=0)

        if(len(args.tickers)!=1):
            for a in axs:
                # a.set_ylim(
                #     [df[df.index > MAGIC_NUMBER].Low[args.ticker].min()*0.95,
                #      df[df.index > MAGIC_NUMBER].High[args.ticker].max()*1.05])
                if args.show_candles:
                    candlestick2_ohlc(a, df["Open"][args.ticker], df["High"][args.ticker], df["Low"][args.ticker], df["Close"][args.ticker], width=0.5, colorup="g", colordown="r",)
            dfRes = create_zig_zag_points(df.Close[args.ticker], df.MinRetracement[args.ticker]).dropna()
            last_price = ticker_df.Close[args.ticker].iloc[-1]
        else:
            for a in axs:
                # a.set_ylim(
                #     [df[df.index > MAGIC_NUMBER].Low.min()*0.95,
                #      df[df.index > MAGIC_NUMBER].High.max()*1.05])
                if args.show_candles:
                    candlestick2_ohlc(a, df["Open"], df["High"], df["Low"], df["Close"], width=0.5, colorup="g", colordown="r",)
            dfRes = create_zig_zag_points(df.Close, df.MinRetracement).dropna()
            last_price = ticker_df.iloc[-1].Close

        # for a in axs:
        #     a.set_xlim([MAGIC_NUMBER,df.index.max()])
        #     cursor = Cursor(a, color="gray", linewidth=1)

        lines = None
        if self.is_sample:
            outfile = f"out/samples/{args.ticker}.png"
            if not args.ticker in SOURCE_LINES: return [None, None, None, None]
            lines = convert_datex(ticker_df, SOURCE_LINES[args.ticker])
        else:
            if args.optimize:
                title = f"optimize/{args.ticker}/-d {args.dif} -r {args.retracement_size}"
            else:
                title = f"output/{args.ticker}"

            outfile = f"out/{title}.png"
            if args.filter:
                dt = datetime.datetime.now().strftime("%y%m%d%H%M")
                outdir = f"out/filtered{dt}/match"
                outdirno = f"out/filtered{dt}/nomatch"
                if not os.path.exists(outdir): os.makedirs(outdir)
                if not os.path.exists(outdirno): os.makedirs(outdirno)
            else:
                if not os.path.exists(os.path.dirname(outfile)):
                    os.makedirs(os.path.dirname(outfile))

        if args.show_zags:
            for a in axs:
                a.plot(dfRes["Value"])
        if not args.no_sr_lines and not lines:
            for a in axs:
                lines = generate_lines(args, a, dfRes)

        if args.ticker in SOURCE_LINES:
            sample_lines = convert_datex(ticker_df, SOURCE_LINES[args.ticker])

        if args.no_boxes:
            draw_lines(axs[0], lines)
            if len(axs) > 1:
                draw_lines( axs[1], sample_lines)

        # log(lines)

        is_in_box = False
        if args.ticker in SOURCE_LINES:
            sample_boxes = convert_lines_to_boxes(sample_lines)
        boxes = []
        if lines and not args.no_boxes:
            if not args.sample_only:
                log("experiment")
            boxes = convert_lines_to_boxes(lines)
            draw_boxes(axs[0], boxes, colors=args.colors)
            log("boxes:", len(boxes))
            log(len(boxes))
            for b in boxes: log(b)
            if len(axs) > 1:
                log("sample")
                draw_boxes(axs[1], sample_boxes)
                log("boxes:", len(sample_boxes))
                for b in boxes: log(b)

        def mydate(x,pos):
            try:
                return df.Date.loc[int(x)]
            except :
                return ''

        # for a in axs:
        #     a.xaxis.set_major_formatter(ti.FuncFormatter(mydate))

        if args.optimize:
            plt.savefig(outfile)
        else:
            # plt.title(ticker)
            if args.filter:
                if is_in_box:
                    # print(args.ticker)
                    outfile = os.path.join(outdir, f"{args.ticker}.png")
                else:
                    outfile = os.path.join(outdirno, f"{args.ticker}.png")
                plt.savefig(outfile)
            else:
                plt.savefig(outfile)
                if args.show: plt.show()

        plt.clf()
        plt.cla()
        plt.close()

        self.outfile = outfile
        self.boxes = boxes
        self.last_price = last_price
        self.price_in_box = False
        if self.is_sample:
            self.sample = outfile

        if args.ticker in SOURCE_LINES:
            self.covered = get_error2(sample_boxes, boxes)

        return self

        # plt.xticks(df.index, labels=df.Date.astype(str))
        # ax.set_xticklabels(labels)
        # plt.xticks(df.index,df.Date)
        # plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d/%Y'))
        # plt.gca().xaxis.set_major_locator(mdates.DayLocator())
        # plt.axis('off')
        # plt.xticks(np.arange(300), ['Tom', 'Dick', 'Sue']*100)
        # ax.set_xticks(df.index, df.Date)
        # df['AvgRng'] = df.Range.rolling(MAGIC_NUMBER).mean()
        # axs[1].plot(ticker_df.MinRetracement)
        # axs[1].plot(ticker_df.Range)
        # axs[2].plot(ticker_df.MaxDiff[ticker])
        # ax.text(.5,.8,f'{ticker} magic:{MAGIC_NUMBER}\nRollingRangeDivClose\nMinRetracement\nMaxDiff', horizontalalignment='center', transform=ax.transAxes)

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
                # log("Support at ", end="")
                # for i in range(len(values) - 1):
                #     log("{:0.2f} and ".format(values[i]), end="")
                # log("{:0.2f} \n".format(values[len(values) - 1]), end="")
                removed_indexes.extend(dropindexes)
                for value in values: sum = sum + value
                if endx > x_max: x_max = endx
                lines.append([startx, endx, sum / len(values)])
    return lines

def draw_boxes(ax, boxes, colors=False):
    colors = colors_(len(boxes))
    counter = 0

    for box in boxes:
        col = colors[counter] if colors else "white"
        ax.add_patch(
            Rectangle(
              (box.x, box.y), box.width, box.height,
              facecolor = col,
              edgecolor = col,)
        )
        counter += 1

def create_zig_zag_points(dfSeries, minRetrace):
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

def draw_lines(ax, lines):
    for line in lines:
        ax.hlines(
            y=line[2],
            xmin=line[0],
            xmax=line[1],
            linewidth=1,
            color="w",
        )

def convert_lines_to_boxes(lines):
    counter = 0
    max_box_x = 0
    boxes = []
    def find_overlapping(lines, line):
        ol = []
        for line2 in lines:
            if line2[0] == line[0] and line2[2] == line[2]: continue
            if line[0] < line2[1] and line[1] > line2[0]: ol.append(line2)
        ol.append(line)
        return ol

    def find_min_x(lines, line):
        ol = find_overlapping(lines, line)
        minx = ol[0][0]
        for line2 in ol:
            if line2[0] < minx:
                minx = line2[0]
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

                if (max_y - min_y) > 2: # minimum size to draw a box TODO
                    width = max_x-min_x
                    height = max_y-min_y
                    boxes.append(Box(x=min_x, y=min_y, width=width, height=height))

    return Box.consolidate(boxes)

def convert_datex(ticker_df, datelines):
    newlines = []
    try:
        for line in datelines:
            newlines.append([
                ticker_df[ticker_df.Date.astype(str) == line[0]].Date.index[0],
                ticker_df[ticker_df.Date.astype(str) == line[1]].Date.index[0],
                line[2]
            ])
    except Exception as e:
        print(e)
        import pdbr; pdbr.set_trace()
        pass

    return newlines

def prepare_df(df, args):
    if(len(args.tickers)!=1):
        t = args.ticker
        df['Range', t] = df.High[t] - df.Low[t]
        df['RollingMax', t] = df.High[t].rolling(MAGIC_NUMBER).max()
        df['RollingMin', t] = df.Low[t].rolling(MAGIC_NUMBER).min()
        df['RollingRangeDivClose', t] = ((df.RollingMax[t] - df.RollingMin[t]) / df.Close[t])
        df['MinRetracement', t] = df.RollingRangeDivClose[t] * args.retracement_size
        df['MaxDiff', t] = df.RollingRangeDivClose[t] * args.dif
    else:
        df['Range'] = df.High - df.Low
        df['RollingMax'] = df.High.rolling(MAGIC_NUMBER).max()
        df['RollingMin'] = df.Low.rolling(MAGIC_NUMBER).min()
        df['RollingRangeDivClose'] = ((df.RollingMax - df.RollingMin) / df.Close)
        df['MinRetracement'] = df.RollingRangeDivClose * args.retracement_size
        df['MaxDiff'] = df.RollingRangeDivClose * args.dif
    return df

SOURCE_LINES= {
    "UPWK": [
        ["2022-05-09","2022-06-16",19.5],
        ["2022-05-11","2022-05-24",16],
    ],
    "ROKU": [
        ["2022-02-18", "2022-03-15", 103],
        ["2022-02-25", "2022-03-29", 138.75],
        ["2022-05-11", "2022-06-15", 77.0],
        ["2022-05-13", "2022-06-08", 100.0],
    ],
    "SHOP": [
        ["2022-05-11", "2022-06-17", 305 ],
        ["2022-05-13", "2022-06-08", 400 ],
    ],
    "ARKK": [
        ['2022-01-24', '2022-02-17', 65.8],
        ['2022-02-01', '2022-02-10', 77.65],
        ['2022-02-28', '2022-04-04', 70.43],
        ['2022-03-14', '2022-05-04', 52],
        ['2022-05-11', '2022-06-14', 36.25],
        ['2022-05-13', '2022-06-09', 45.65],
    ],
    "TSLA": [
        ['2022-05-13', '2022-06-02', 773.7],
        ['2022-05-24', '2022-06-16', 630],
    ],
    "ZM": [
        ['2022-03-14', '2022-05-13', 94.81],
        ['2022-03-22', '2022-06-16', 119.7],
    ],
}

def get_error2(sample_boxes, boxes):
    last_x_box = sample_boxes[0]
    area = last_x_box.height * last_x_box.width
    max_overlap = 0
    for box in boxes:
        overlapx = overlap(
            box.x, (box.x + box.width),
            last_x_box.x, (last_x_box.x + last_x_box.width))
        overlapy = overlap(
            box.y, (box.y + box.height),
            last_x_box.y, (last_x_box.y + last_x_box.height))
        ol = overlapx * overlapy
        if ol > max_overlap: max_overlap = ol
    return max_overlap/area

def measure_error(x,y):
    return imgcompare.image_diff_percent(x, y)
