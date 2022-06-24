import pandas as pd
from platform import system
from matplotlib.widgets import Cursor
import random

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
from pandas_datareader.yahoo.headers import DEFAULT_HEADERS
import requests_cache
from mplfinance.original_flavor import candlestick2_ohlc
from argparse import ArgumentParser
import imgcompare
from imgcompare import is_equal
import os
from PIL import Image
from matplotlib.patches import Rectangle

expire_after = datetime.timedelta(days=3)
session = requests_cache.CachedSession('yfinance.cache')
    # cache_name='cache', backend='sqlite', expire_after=expire_after)
session.headers = DEFAULT_HEADERS

# fmt: off
AAYUSH_TICKERS = [
    "AAPL",
    "ARKK",
    "GOOGL",
    "PDD",
    "QQQ",
    "ROKU",
    "SPY",
    "TSLA",
    "ZM",
]
ALL_TICKERS = ["MMM", "ABT", "ABBV", "ABMD", "ACN", "ATVI", "ADBE", "AMD",
               "AAP", "AES", "AFL", "A", "APD", "AKAM", "ALK", "ALB", "ARE",
               "ALGN", "ALLE", "LNT", "ALL", "GOOGL", "GOOG", "MO", "AMZN",
               "AMCR", "AEE", "AAL", "AEP", "AXP", "AIG", "AMT", "AWK", "AMP",
               "ABC", "AME", "AMGN", "APH", "ADI", "ANSS", "ANTM", "AON", "AOS",
               "APA", "AIV", "AAPL", "AMAT", "APTV", "ADM", "ANET", "AJG",
               "AIZ", "T", "ATO", "ADSK", "ADP", "AZO", "AVB", "AVY", "BKR",
               "BLL", "BAC", "BK", "BAX", "BDX", "BRK-B", "BBY", "BIO", "BIIB",
               "BLK", "BA", "BKNG", "BWA", "BXP", "BMY", "AVGO", "BR",
               "BF-B", "CHRW", "CDNS", "CPB", "COF", "CAH", "KMX", "CCL",
               "CARR", "CAT", "CBOE", "CBRE", "CDW", "CE", "CNC", "CNP", "CERN",
               "CF", "SCHW", "CHTR", "CVX", "CMG", "CB", "CHD", "CI", "CINF",
               "CTAS", "CSCO", "C", "CFG", "CTXS", "CLX", "CME", "CMS", "KO",
               "CTSH", "CL", "CMCSA", "CMA", "CAG", "COP", "ED", "STZ", "COO",
               "CPRT", "GLW", "CTVA", "COST", "COTY", "CCI", "CSX", "CMI",
               "CVS", "DHI", "DHR", "DRI", "DVA", "DE", "DAL", "XRAY", "DVN",
               "DXCM", "FANG", "DLR", "DFS", "DISH", "DG", "DLTR", "D", "DPZ",
               "DOV", "DOW", "DTE", "DUK", "DRE", "DD", "DXC", "EMN", "ETN",
               "EBAY", "ECL", "EIX", "EW", "EA", "EMR", "ETR", "EOG", "EFX",
               "EQIX", "EQR", "ESS", "EL", "EVRG", "ES", "RE", "EXC", "EXPE",
               "EXPD", "EXR", "XOM", "FFIV", "FB", "FAST", "FRT", "FDX", "FIS",
               "FITB", "FE", "FRC", "FISV", "FLT", "FLS", "FMC", "F", "FTNT",
               "FTV", "FBHS", "FOXA", "FOX", "BEN", "FCX", "GPS", "GRMN", "IT",
               "GD", "GE", "GIS", "GM", "GPC", "GILD", "GL", "GPN", "GS", "GWW",
               "HRB", "HAL", "HBI", "HIG", "HAS", "HCA", "PEAK", "HSIC", "HSY",
               "HES", "HPE", "HLT", "HOLX", "HD", "HON", "HRL", "HST", "HWM",
               "HPQ", "HUM", "HBAN", "HII", "IEX", "IDXX", "ITW", "ILMN",
               "INCY", "IR", "INTC", "ICE", "IBM", "IP", "IPG", "IFF", "INTU",
               "ISRG", "IVZ", "IPGP", "IQV", "IRM", "JKHY", "J", "JBHT", "SJM",
               "JNJ", "JCI", "JPM", "JNPR", "K", "KEY", "KEYS", "KMB", "KIM",
               "KMI", "KLAC", "KSS", "KHC", "KR", "LHX", "LH", "LRCX", "LW",
               "LVS", "LEG", "LDOS", "LEN", "LLY", "LNC", "LIN", "LYV", "LKQ",
               "LMT", "L", "LOW", "LYB", "MTB", "MRO", "MPC", "MKTX", "MAR",
               "MMC", "MLM", "MAS", "MA", "MKC", "MCD", "MCK", "MDT", "MRK",
               "MET", "MTD", "MGM", "MCHP", "MU", "MSFT", "MAA", "MHK", "TAP",
               "MDLZ", "MNST", "MCO", "MS", "MOS", "MSI", "MSCI", "NDAQ", "NOV",
               "NTAP", "NFLX", "NWL", "NEM", "NWSA", "NWS", "NEE", "NLSN",
               "NKE", "NI", "NSC", "NTRS", "NOC", "NLOK", "NCLH", "NRG", "NUE",
               "NVDA", "NVR", "ORLY", "OXY", "ODFL", "OMC", "OKE", "ORCL",
               "OTIS", "PCAR", "PKG", "PH", "PAYX", "PAYC", "PYPL", "PNR",
               "PEP", "PKI", "PRGO", "PFE", "PM", "PSX", "PNW", "PXD", "PNC",
               "PPG", "PPL", "PFG", "PG", "PGR", "PLD", "PRU", "PEG", "PSA",
               "PHM", "PVH", "QRVO", "PWR", "QCOM", "DGX", "RL", "RJF", "RTX",
               "O", "REG", "REGN", "RF", "RSG", "RMD", "RHI", "ROK", "ROL",
               "ROP", "ROST", "RCL", "SPGI", "CRM", "SBAC", "SLB", "STX", "SEE",
               "SRE", "NOW", "SHW", "SPG", "SWKS", "SLG", "SNA", "SO", "LUV",
               "SWK", "SBUX", "STT", "STE", "SYK", "SIVB", "SYF", "SNPS", "SYY",
               "TMUS", "TROW", "TTWO", "TPR", "TGT", "TEL", "FTI", "TDY", "TFX",
               "TXN", "TXT", "TMO", "TJX", "TSCO", "TT", "TDG", "TRV", "TFC",
               "TWTR", "TYL", "TSN", "UDR", "ULTA", "USB", "UAA", "UA", "UNP",
               "UAL", "UNH", "UPS", "URI", "UHS", "UNM", "VFC", "VLO", "VTR",
               "VRSN", "VRSK", "VZ", "VRTX", "V", "VNO", "VMC", "WRB", "WAB",
               "WMT", "WBA", "DIS", "WM", "WAT", "WEC", "WFC", "WELL", "WST",
               "WDC", "WU", "WRK", "WY", "WHR", "WMB", "WYNN", "XEL", "XRX",
               "XYL", "YUM", "ZBRA", "ZBH", "ZION", "ZTS",]
# fmt: on
MAGIC_NUMBER = 50
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

def get_data(args):
    ticker_df = web.get_data_yahoo(
        args.tickers, period=args.period, interval=args.interval, session=session
    )
    if args.start_date:
        ticker_df = ticker_df[args.start_date :]
    if args.stop_date:
        ticker_df = ticker_df[: args.stop_date]
    return ticker_df.reset_index()

def log(*argv, **kwargs):
    if os.environ['SRCLI_VERBOSE']:
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

def draw_boxes(ax, boxes):
    colors_ = lambda n: list(map(lambda i: "#" + "%06x" % random.randint(0, 0xFFFFFF),range(n)))
    colors = colors_(len(boxes))
    counter = 0
    for box in boxes:
        ax.add_patch(
            Rectangle(
              (box.x, box.y), box.width, box.height,
              facecolor = "white",
              edgecolor = "white",)
        )
        counter += 1

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

def draw_lines(ax, lines):
    for line in lines:
        ax.hlines(
            y=line[2],
            xmin=line[0],
            xmax=line[1],
            linewidth=1,
            color="w",
        )

def draw_chart(ticker_df, args, sample=False):
    log("\n\n" + args.ticker)
    df = prepare_df(ticker_df, args)

    if args.side_by_side:
        fig, axs = plt.subplots(
            1, 2,
            facecolor=(0,0,0),
            sharex=True,
            sharey=False,
            figsize=(15, 8),
            num=args.ticker,)
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
            a.set_ylim(
                [df[df.index > MAGIC_NUMBER].Low[args.ticker].min()*0.95,
                 df[df.index > MAGIC_NUMBER].High[args.ticker].max()*1.05])
            if not args.no_candles:
                candlestick2_ohlc(a, df["Open"][args.ticker], df["High"][args.ticker], df["Low"][args.ticker], df["Close"][args.ticker], width=0.5, colorup="g", colordown="r",)
        dfRes = createZigZagPoints(df.Close[args.ticker], df.MinRetracement[args.ticker]).dropna()
    else:
        for a in axs:
            a.set_ylim(
                [df[df.index > MAGIC_NUMBER].Low.min()*0.95,
                 df[df.index > MAGIC_NUMBER].High.max()*1.05])
            if not args.no_candles:
                candlestick2_ohlc(a, df["Open"], df["High"], df["Low"], df["Close"], width=0.5, colorup="g", colordown="r",)
        dfRes = createZigZagPoints(df.Close, df.MinRetracement).dropna()

    for a in axs:
        a.set_xlim([MAGIC_NUMBER,df.index.max()])
        cursor = Cursor(a, color="gray", linewidth=1)

    lines = None
    if sample:
        outfile = f"out/samples/{args.ticker}.png"
        lines = convert_datex(ticker_df, SOURCE_LINES[args.ticker])
    else:
        title = f"{args.ticker}/-d {args.dif} -r {args.retracement_size}"
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
    sample_lines = convert_datex(ticker_df, SOURCE_LINES[args.ticker])


    if not args.draw_boxes:
        draw_lines(axs[0], lines)
        if len(axs) > 1:
            draw_lines( axs[1], sample_lines)

    log(lines)

    is_in_box = False
    if lines and args.draw_boxes:
        if not args.sample_only:
            print("experiment")
        # print(lines)
        boxes = convert_lines_to_boxes(lines)
        draw_boxes(axs[0], boxes)
        print("boxes:", len(boxes))
        print(len(boxes))
        for b in boxes: print(b)
        # import pdbr; pdbr.set_trace()
        if len(axs) > 1:
            print("sample")
            boxes = convert_lines_to_boxes(sample_lines)
            draw_boxes(axs[1], boxes)
            print("boxes:", len(boxes))
            for b in boxes: print(b)

    import matplotlib.ticker as ti
    def mydate(x,pos):
        try:
            return df.Date.loc[int(x)]
        except :
            return ''

    for a in axs:
        a.xaxis.set_major_formatter(ti.FuncFormatter(mydate))

    # get_error2(ticker_df, SOURCE_LINES[args.ticker])

    if args.optimize:
        plt.savefig(outfile)
    else:
        # plt.title(ticker)
        if args.filter:
            if is_in_box:
                print(args.ticker)
                outfile = os.path.join(outdir, f"{args.ticker}.png")
            else:
                outfile = os.path.join(outdirno, f"{args.ticker}.png")
            plt.savefig(outfile)
        else:
            plt.show()


    plt.clf()
    plt.cla()
    plt.close()
    return outfile

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

def get_error2(ticker_df, lines, ticker):
    source = convert_datex(ticker_df, lines)
    # import pdbr; pdbr.set_trace()
    pass

def measure_error(x,y):
    return imgcompare.image_diff_percent(x, y)

class Box():
    x: float
    y: float
    width: float
    height: float

    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def __repr__(self):
        return f"({self.x}, {self.y}), {self.width}, {self.height}"

    # def find_overlapping(lines, line):
    #     ol = []
    #     for line2 in lines:
    #         if line2[0] == line[0] and line2[2] == line[2]: continue
    #         if line[0] < line2[1] and line[1] > line2[0]: ol.append(line2)
    #     return ol
    #
    # def find_min_x(lines, line):
    #     ol = find_overlapping(lines, line)
    #     minx = ol[0][0]
    #     for line2 in ol:
    #         if line2[0] < minx: minx = line2[0]
    #     return minx

    def does_contain(box1, box2):
        # does x overlap?
        min_x = min(box1.x, box2.x)
        # find the lowest y value

    def x_values_overlap(box1, box2):
        if box1.x == box2.x:
            return True
        if (box1.x < box2.x) and ((box1.x + box1.width) > box2.x):
            return True
        if (box2.x < box1.x) and ((box2.x + box2.width) > box1.x):
            return True
        return False

    def consolidate(boxes):
        cboxes = []
        for box in boxes:
            # if none add it
            if len(cboxes) == 0:
                cboxes.append(box)

            # look for any that can be extended
            extended = False
            for box2 in cboxes:
                if box.y == box2.y and Box.x_values_overlap(box, box2):
                    extended = True
                    box2.height = max(box.height, box2.height)
                    box2.width = max(box.width, box2.width)

            if not extended:
                cboxes.append(box)

        return cboxes

def convert_lines_to_boxes(lines):
    counter = 0
    max_box_x = 0
    boxes = []
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
                if (max_y - min_y) > 2:
                    if max_x > max_box_x:
                        max_box_x = max_x
                        last_box_max_y = max_y
                        last_box_min_y = min_y

                    boxes.append(Box(x=min_x, y=min_y, width=max_x-min_x, height=max_y-min_y))

    # return boxes
    return Box.consolidate(boxes)
    # is_in_box = False
    #
    # if max_box_x:
    #     if(len(args.tickers)!=1):
    #         mbd = ticker_df.loc[max_box_x].Date[0]
    #         md = ticker_df.loc[ticker_df.index.max()].Date[0]
    #         current_price = ticker_df.loc[ticker_df.index.max()].Close[args.ticker]
    #     else:
    #         mbd = ticker_df.loc[max_box_x].Date
    #         md = ticker_df.loc[ticker_df.index.max()].Date
    #         current_price = ticker_df.loc[ticker_df.index.max()].Close
    #
    #     diff = (md - mbd).days
    #     is_in_last_box_range = (current_price > last_box_min_y) and (current_price < last_box_max_y)
    #     is_in_box = (is_in_last_box_range) and diff <= 10
    # else:
    #     is_in_box = False
    #
    # return [is_in_box, boxes]

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
