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
SOURCE_LINES= {
    "UPWK": [[132,158,16], [132,158,19.95],], #--start-date=2021-11-01 --stop-date=2022-06-18
    "ARKK": [[57,66,68.5], [63,70,77],
             [81,106,71.37], [91,120,52.25],
             [133,155,36.0],[145,151,46.02],] #--start-date=2021-11-01 --stop-date=2022-06-18
}

def measure_error(x,y):
    return imgcompare.image_diff_percent(x, y)

def log(*argv, **kwargs):
    if args.verbose:
        print(*argv, **kwargs)

def draw_sr_lines(ax, dfRes):
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
                    if (
                        args.target_max
                        and values[i] < args.target_max
                        and values[i] > args.target_min
                    ):
                        has_line_near_target = True

                    log("{:0.2f} and ".format(values[i]), end="")
                log("{:0.2f} \n".format(values[len(values) - 1]), end="")
                removed_indexes.extend(dropindexes)
                for value in values: sum = sum + value
                if endx > x_max: x_max = endx
                lines.append([startx, endx, sum / len(values)])
                if not args.draw_boxes:
                    ax.hlines(
                        y=sum / len(values),
                        xmin=startx,
                        xmax=endx,
                        linewidth=1,
                        color="w",
                    )
    return lines

def draw_boxes(ax, lines):
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

def prepare_df(df):
    df['Range'] = df.High - df.Low
    df['RollingMax'] = df.High.rolling(MAGIC_NUMBER).max()
    df['RollingMin'] = df.Low.rolling(MAGIC_NUMBER).min()
    df['RollingRangeDivClose'] = ((df.RollingMax - df.RollingMin) / df.Close)
    df['MinRetracement'] = df.RollingRangeDivClose * args.retracement_size
    df['MaxDiff'] = df.RollingRangeDivClose * args.dif
    return df

def draw_chart(args, lines=None):
    # df['AvgRng'] = df.Range.rolling(MAGIC_NUMBER).mean()
    # axs[1].plot(ticker_df.MinRetracement)
    # axs[1].plot(ticker_df.Range)
    # ax.plot(dfRes["Value"])
    # axs[2].plot(ticker_df.MaxDiff[ticker])
    # ax.text(.5,.8,f'{ticker} magic:{MAGIC_NUMBER}\nRollingRangeDivClose\nMinRetracement\nMaxDiff', horizontalalignment='center', transform=ax.transAxes)

    log("\n\n" + ticker)
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
    df = prepare_df(ticker_df)
    cursor = Cursor(ax, color="gray", linewidth=1)

    if lines:
        outfile = f"data/samples/{args.ticker}.png"
    else:
        title = f"{ticker}/-d {args.dif} -r {args.retracement_size}"
        outfile = f"out/{title}.png"
        if not os.path.exists(os.path.dirname(outfile)):
            os.makedirs(os.path.dirname(outfile))

    dfRes = createZigZagPoints(df.Close, df.MinRetracement).dropna()
    if not args.no_candles:
        print("drawing candles")
        candlestick2_ohlc(ax, df["Open"], df["High"], df["Low"], df["Close"], width=0.5, colorup="g", colordown="r",)

    if not args.no_sr_lines and not lines:
        lines = draw_sr_lines(ax, dfRes)

    log(lines)

    if args.draw_boxes:
        print(lines)
        draw_boxes(ax, lines)

    # plt.xticks(df.index, labels=df.Date.astype(str))
    # ax.set_xticklabels(labels)
    # plt.xticks(df.index,df.Date)
    # ax.set_ylim([df.Low.min()*0.95, df.High.max()*1.05])
    # ax.set_xlim([MAGIC_NUMBER,df.index.max()])

    # import pdbr; pdbr.set_trace()
    # plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d/%Y'))
    # plt.gca().xaxis.set_major_locator(mdates.DayLocator())
    # plt.axis('off')
    # plt.xticks(np.arange(300), ['Tom', 'Dick', 'Sue']*100)
    # ax.set_xticks(df.index, df.Date)

    # import matplotlib.ticker as ti
    # def mydate(x,pos):
    #     try:
    #         return df.Date.loc[int(x)]
    #     except :
    #         return ''
    # ax.xaxis.set_major_formatter(ti.FuncFormatter(mydate))

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

parser = ArgumentParser(description="Algorithmic Support and Resistance")
parser.add_argument(
    "-t",
    "--tickers",
    default="ROKU",
    type=str,
    required=False,
    # help="Used to look up a specific tickers. Commma seperated. Example: MSFT,AAPL,AMZN default: List of S&P 500 companies",
    help="Used to look up a specific tickers.",
)
parser.add_argument(
    "-p",
    "--period",
    default="5y",
    type=str,
    required=False,
    help="Period to look back. valid periods: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max. default: 5y",
)
parser.add_argument(
    "-i",
    "--interval",
    default="1d",
    type=str,
    required=False,
    help="Interval of each bar. valid intervals: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo. default: 1d",
)
parser.add_argument(
    "-d",
    "--dif",
    default="10",
    type=float,
    required=False,
    help="Max %% difference between two points to group them together. Default: 10",
)
parser.add_argument(
    "-r",
    "--retracement-size",
    default="10",
    type=float,
    required=False,
    help="Segment Size Minimum %",
)
parser.add_argument(
    "--time",
    default="365",
    type=int,
    required=False,
    help="Max time measured in number of bars between two points to be grouped together. Default: 150",
)
parser.add_argument(
    "-n",
    "--number",
    default="2",
    type=int,
    required=False,
    help="Min number of points in price range to draw a support/resistance line.  Default: 2",
)
parser.add_argument(
    "-m",
    "--min",
    default="10",
    type=int,
    required=False,
    help="Min number of bars from the start the support/resistance line has to be at to display chart. Default: 150",
)

parser.add_argument(
    "--title",
    type=str,
    required=False,
    help="Title of the file to save the chart to",
)
parser.add_argument(
    "--start-date",
    type=str,
    required=False,
    help="Start Date",
)
parser.add_argument(
    "--target-max",
    type=float,
    required=False,
    help="Target S/R level to filter",
)
parser.add_argument(
    "--target-min",
    type=float,
    required=False,
    help="Target S/R level to filter",
)
parser.add_argument(
    "--stop-date",
    type=str,
    required=False,
    help="Stop Date",
)
parser.add_argument(
    "--optimize",
    action="store_true",
    required=False,
    help="Run many variables and save file (wont display)",
)
parser.add_argument(
    "--no-candles",
    action="store_true",
    required=False,
    help="Dont show candlesticks",
)
parser.add_argument(
    "--no-sr-lines",
    action="store_true",
    required=False,
    help="Dont show s/r lines",
)
parser.add_argument(
    "--draw-boxes",
    action="store_true",
    required=False,
    help="Draw boxes",
)
parser.add_argument(
    "--empty-boxes",
    action="store_true",
    required=False,
    help="Don't fill boxes",
)
parser.add_argument(
    "-v",
    "--verbose",
    action="store_true",
    required=False,
    help="Verbose",
)
args = parser.parse_args()

# S&P 500 Tickers
# fmt: off
if args.tickers == "SPY500":
    tickers = ["MMM", "ABT", "ABBV", "ABMD", "ACN", "ATVI", "ADBE", "AMD", "AAP", "AES", "AFL", "A", "APD", "AKAM", "ALK", "ALB", "ARE", "ALXN", "ALGN", "ALLE", "LNT", "ALL", "GOOGL", "GOOG", "MO", "AMZN", "AMCR", "AEE", "AAL", "AEP", "AXP", "AIG", "AMT", "AWK", "AMP", "ABC", "AME", "AMGN", "APH", "ADI", "ANSS", "ANTM", "AON", "AOS", "APA", "AIV", "AAPL", "AMAT", "APTV", "ADM", "ANET", "AJG", "AIZ", "T", "ATO", "ADSK", "ADP", "AZO", "AVB", "AVY", "BKR", "BLL", "BAC", "BK", "BAX", "BDX", "BRK-B", "BBY", "BIO", "BIIB", "BLK", "BA", "BKNG", "BWA", "BXP", "BSX", "BMY", "AVGO", "BR", "BF-B", "CHRW", "COG", "CDNS", "CPB", "COF", "CAH", "KMX", "CCL", "CARR", "CAT", "CBOE", "CBRE", "CDW", "CE", "CNC", "CNP", "CTL", "CERN", "CF", "SCHW", "CHTR", "CVX", "CMG", "CB", "CHD", "CI", "CINF", "CTAS", "CSCO", "C", "CFG", "CTXS", "CLX", "CME", "CMS", "KO", "CTSH", "CL", "CMCSA", "CMA", "CAG", "CXO", "COP", "ED", "STZ", "COO", "CPRT", "GLW", "CTVA", "COST", "COTY", "CCI", "CSX", "CMI", "CVS", "DHI", "DHR", "DRI", "DVA", "DE", "DAL", "XRAY", "DVN", "DXCM", "FANG", "DLR", "DFS", "DISCA", "DISCK", "DISH", "DG", "DLTR", "D", "DPZ", "DOV", "DOW", "DTE", "DUK", "DRE", "DD", "DXC", "ETFC", "EMN", "ETN", "EBAY", "ECL", "EIX", "EW", "EA", "EMR", "ETR", "EOG", "EFX", "EQIX", "EQR", "ESS", "EL", "EVRG", "ES", "RE", "EXC", "EXPE", "EXPD", "EXR", "XOM", "FFIV", "FB", "FAST", "FRT", "FDX", "FIS", "FITB", "FE", "FRC", "FISV", "FLT", "FLIR", "FLS", "FMC", "F", "FTNT", "FTV", "FBHS", "FOXA", "FOX", "BEN", "FCX", "GPS", "GRMN", "IT", "GD", "GE", "GIS", "GM", "GPC", "GILD", "GL", "GPN", "GS", "GWW", "HRB", "HAL", "HBI", "HIG", "HAS", "HCA", "PEAK", "HSIC", "HSY", "HES", "HPE", "HLT", "HFC", "HOLX", "HD", "HON", "HRL", "HST", "HWM", "HPQ", "HUM", "HBAN", "HII", "IEX", "IDXX", "INFO", "ITW", "ILMN", "INCY", "IR", "INTC", "ICE", "IBM", "IP", "IPG", "IFF", "INTU", "ISRG", "IVZ", "IPGP", "IQV", "IRM", "JKHY", "J", "JBHT", "SJM", "JNJ", "JCI", "JPM", "JNPR", "KSU", "K", "KEY", "KEYS", "KMB", "KIM", "KMI", "KLAC", "KSS", "KHC", "KR", "LB", "LHX", "LH", "LRCX", "LW", "LVS", "LEG", "LDOS", "LEN", "LLY", "LNC", "LIN", "LYV", "LKQ", "LMT", "L", "LOW", "LYB", "MTB", "MRO", "MPC", "MKTX", "MAR", "MMC", "MLM", "MAS", "MA", "MKC", "MXIM", "MCD", "MCK", "MDT", "MRK", "MET", "MTD", "MGM", "MCHP", "MU", "MSFT", "MAA", "MHK", "TAP", "MDLZ", "MNST", "MCO", "MS", "MOS", "MSI", "MSCI", "MYL", "NDAQ", "NOV", "NTAP", "NFLX", "NWL", "NEM", "NWSA", "NWS", "NEE", "NLSN", "NKE", "NI", "NBL", "NSC", "NTRS", "NOC", "NLOK", "NCLH", "NRG", "NUE", "NVDA", "NVR", "ORLY", "OXY", "ODFL", "OMC", "OKE", "ORCL", "OTIS", "PCAR", "PKG", "PH", "PAYX", "PAYC", "PYPL", "PNR", "PBCT", "PEP", "PKI", "PRGO", "PFE", "PM", "PSX", "PNW", "PXD", "PNC", "PPG", "PPL", "PFG", "PG", "PGR", "PLD", "PRU", "PEG", "PSA", "PHM", "PVH", "QRVO", "PWR", "QCOM", "DGX", "RL", "RJF", "RTX", "O", "REG", "REGN", "RF", "RSG", "RMD", "RHI", "ROK", "ROL", "ROP", "ROST", "RCL", "SPGI", "CRM", "SBAC", "SLB", "STX", "SEE", "SRE", "NOW", "SHW", "SPG", "SWKS", "SLG", "SNA", "SO", "LUV", "SWK", "SBUX", "STT", "STE", "SYK", "SIVB", "SYF", "SNPS", "SYY", "TMUS", "TROW", "TTWO", "TPR", "TGT", "TEL", "FTI", "TDY", "TFX", "TXN", "TXT", "TMO", "TIF", "TJX", "TSCO", "TT", "TDG", "TRV", "TFC", "TWTR", "TYL", "TSN", "UDR", "ULTA", "USB", "UAA", "UA", "UNP", "UAL", "UNH", "UPS", "URI", "UHS", "UNM", "VFC", "VLO", "VAR", "VTR", "VRSN", "VRSK", "VZ", "VRTX", "VIAC", "V", "VNO", "VMC", "WRB", "WAB", "WMT", "WBA", "DIS", "WM", "WAT", "WEC", "WFC", "WELL", "WST", "WDC", "WU", "WRK", "WY", "WHR", "WMB", "WLTW", "WYNN", "XEL", "XRX", "XLNX", "XYL", "YUM", "ZBRA", "ZBH", "ZION", "ZTS"]
else:
    tickers = args.tickers.split(",")
# fmt: on

if __name__ == "__main__":
    if args.no_sr_lines:
        difs = [11]
    else:
        difs = range(5, 15)

    for ticker in tickers:
        ticker_df = web.get_data_yahoo(
            ticker, period=args.period, interval=args.interval
        )
        if args.start_date:
            ticker_df = ticker_df[args.start_date :]
        if args.stop_date:
            ticker_df = ticker_df[: args.stop_date]
        ticker_df = ticker_df.reset_index()

        errors = []
        args.ticker = ticker

        if args.optimize:
            sample = Image.open(draw_chart(args, SOURCE_LINES[ticker])).convert('RGB')

            for dif in difs:
                for ret in range(9, 15):
                    for num in [2]:
                        # if dif < seg: continue
                        args.retracement_size = ret
                        args.dif = dif
                        args.number = num
                        outfile = draw_chart(args)
                        if os.path.exists(outfile):
                            new = Image.open(outfile).convert('RGB')
                            error = measure_error(sample, new)
                            # print("err", error)
                            errors.append([ticker, dif, ret, num, outfile, error])

            df = pd.read_csv('data/samples.csv')
            df = df.drop(df[df.symbol == ticker].index)
            df1 = pd.DataFrame(errors, columns=['symbol', 'dif','ret','num', 'outfile', 'err', ])
            pd.concat([df1, df]).to_csv(f'data/samples.csv', index=False)
        else:
            draw_chart(args)
