import pandas as pd
from platform import system
from matplotlib.widgets import Cursor

pd.core.common.is_list_like = pd.api.types.is_list_like
import pandas_datareader.data as web
import numpy as np
from matplotlib.dates import date2num, DayLocator, DateFormatter
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
    "--no-candle",
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
args = parser.parse_args()

# S&P 500 Tickers
# fmt: off
if args.tickers == "SPY500":
    tickers = ["MMM", "ABT", "ABBV", "ABMD", "ACN", "ATVI", "ADBE", "AMD", "AAP", "AES", "AFL", "A", "APD", "AKAM", "ALK", "ALB", "ARE", "ALXN", "ALGN", "ALLE", "LNT", "ALL", "GOOGL", "GOOG", "MO", "AMZN", "AMCR", "AEE", "AAL", "AEP", "AXP", "AIG", "AMT", "AWK", "AMP", "ABC", "AME", "AMGN", "APH", "ADI", "ANSS", "ANTM", "AON", "AOS", "APA", "AIV", "AAPL", "AMAT", "APTV", "ADM", "ANET", "AJG", "AIZ", "T", "ATO", "ADSK", "ADP", "AZO", "AVB", "AVY", "BKR", "BLL", "BAC", "BK", "BAX", "BDX", "BRK-B", "BBY", "BIO", "BIIB", "BLK", "BA", "BKNG", "BWA", "BXP", "BSX", "BMY", "AVGO", "BR", "BF-B", "CHRW", "COG", "CDNS", "CPB", "COF", "CAH", "KMX", "CCL", "CARR", "CAT", "CBOE", "CBRE", "CDW", "CE", "CNC", "CNP", "CTL", "CERN", "CF", "SCHW", "CHTR", "CVX", "CMG", "CB", "CHD", "CI", "CINF", "CTAS", "CSCO", "C", "CFG", "CTXS", "CLX", "CME", "CMS", "KO", "CTSH", "CL", "CMCSA", "CMA", "CAG", "CXO", "COP", "ED", "STZ", "COO", "CPRT", "GLW", "CTVA", "COST", "COTY", "CCI", "CSX", "CMI", "CVS", "DHI", "DHR", "DRI", "DVA", "DE", "DAL", "XRAY", "DVN", "DXCM", "FANG", "DLR", "DFS", "DISCA", "DISCK", "DISH", "DG", "DLTR", "D", "DPZ", "DOV", "DOW", "DTE", "DUK", "DRE", "DD", "DXC", "ETFC", "EMN", "ETN", "EBAY", "ECL", "EIX", "EW", "EA", "EMR", "ETR", "EOG", "EFX", "EQIX", "EQR", "ESS", "EL", "EVRG", "ES", "RE", "EXC", "EXPE", "EXPD", "EXR", "XOM", "FFIV", "FB", "FAST", "FRT", "FDX", "FIS", "FITB", "FE", "FRC", "FISV", "FLT", "FLIR", "FLS", "FMC", "F", "FTNT", "FTV", "FBHS", "FOXA", "FOX", "BEN", "FCX", "GPS", "GRMN", "IT", "GD", "GE", "GIS", "GM", "GPC", "GILD", "GL", "GPN", "GS", "GWW", "HRB", "HAL", "HBI", "HIG", "HAS", "HCA", "PEAK", "HSIC", "HSY", "HES", "HPE", "HLT", "HFC", "HOLX", "HD", "HON", "HRL", "HST", "HWM", "HPQ", "HUM", "HBAN", "HII", "IEX", "IDXX", "INFO", "ITW", "ILMN", "INCY", "IR", "INTC", "ICE", "IBM", "IP", "IPG", "IFF", "INTU", "ISRG", "IVZ", "IPGP", "IQV", "IRM", "JKHY", "J", "JBHT", "SJM", "JNJ", "JCI", "JPM", "JNPR", "KSU", "K", "KEY", "KEYS", "KMB", "KIM", "KMI", "KLAC", "KSS", "KHC", "KR", "LB", "LHX", "LH", "LRCX", "LW", "LVS", "LEG", "LDOS", "LEN", "LLY", "LNC", "LIN", "LYV", "LKQ", "LMT", "L", "LOW", "LYB", "MTB", "MRO", "MPC", "MKTX", "MAR", "MMC", "MLM", "MAS", "MA", "MKC", "MXIM", "MCD", "MCK", "MDT", "MRK", "MET", "MTD", "MGM", "MCHP", "MU", "MSFT", "MAA", "MHK", "TAP", "MDLZ", "MNST", "MCO", "MS", "MOS", "MSI", "MSCI", "MYL", "NDAQ", "NOV", "NTAP", "NFLX", "NWL", "NEM", "NWSA", "NWS", "NEE", "NLSN", "NKE", "NI", "NBL", "NSC", "NTRS", "NOC", "NLOK", "NCLH", "NRG", "NUE", "NVDA", "NVR", "ORLY", "OXY", "ODFL", "OMC", "OKE", "ORCL", "OTIS", "PCAR", "PKG", "PH", "PAYX", "PAYC", "PYPL", "PNR", "PBCT", "PEP", "PKI", "PRGO", "PFE", "PM", "PSX", "PNW", "PXD", "PNC", "PPG", "PPL", "PFG", "PG", "PGR", "PLD", "PRU", "PEG", "PSA", "PHM", "PVH", "QRVO", "PWR", "QCOM", "DGX", "RL", "RJF", "RTX", "O", "REG", "REGN", "RF", "RSG", "RMD", "RHI", "ROK", "ROL", "ROP", "ROST", "RCL", "SPGI", "CRM", "SBAC", "SLB", "STX", "SEE", "SRE", "NOW", "SHW", "SPG", "SWKS", "SLG", "SNA", "SO", "LUV", "SWK", "SBUX", "STT", "STE", "SYK", "SIVB", "SYF", "SNPS", "SYY", "TMUS", "TROW", "TTWO", "TPR", "TGT", "TEL", "FTI", "TDY", "TFX", "TXN", "TXT", "TMO", "TIF", "TJX", "TSCO", "TT", "TDG", "TRV", "TFC", "TWTR", "TYL", "TSN", "UDR", "ULTA", "USB", "UAA", "UA", "UNP", "UAL", "UNH", "UPS", "URI", "UHS", "UNM", "VFC", "VLO", "VAR", "VTR", "VRSN", "VRSK", "VZ", "VRTX", "VIAC", "V", "VNO", "VMC", "WRB", "WAB", "WMT", "WBA", "DIS", "WM", "WAT", "WEC", "WFC", "WELL", "WST", "WDC", "WU", "WRK", "WY", "WHR", "WMB", "WLTW", "WYNN", "XEL", "XRX", "XLNX", "XYL", "YUM", "ZBRA", "ZBH", "ZION", "ZTS"]
else:
    tickers = args.tickers.split(",")
# fmt: on

connected = False
while not connected:
    try:
        ticker_df = web.get_data_yahoo(
            tickers, period=args.period, interval=args.interval
        )
        if args.start_date:
            ticker_df = ticker_df[args.start_date :]
        if args.stop_date:
            ticker_df = ticker_df[: args.stop_date]
        ticker_df = ticker_df.reset_index()
        connected = True
    except Exception as e:
        print("type error: " + str(e))
        time.sleep(5)
        pass


def run(args):
    for ticker in tickers:
        print("\n\n" + ticker)
        try:
            if args.optimize:
                # title = f"{ticker}/{args.title}"
                # title = f"{ticker}/-r {args.retracement_size} -d {args.dif}"
                title = f"{ticker}/-d {args.dif} -r {args.retracement_size}"
                # title = f"{ticker}/-d {args.dif}"
                outfile = f"out/{title}.jpg"
                if path.exists(outfile):
                    print("skipping", outfile)
                    return
                else:
                    print("\n\ncreating", outfile)

            x_max = 0
            # fig, ax = plt.figure(facecolor=(1, 1, 1), figsize=(15, 8),)
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
            # axs[1].yaxis.tick_right()
            # axs[2].yaxis.tick_right()
            # cursor = Cursor(axs, color="gray", linewidth=1)
            fig.tight_layout()
            fig.subplots_adjust(wspace=0, hspace=0)

            # ticker_df['AvgRng'] = ticker_df.Range.rolling(MAGIC_NUMBER).mean()

            MAGIC_NUMBER = 50

            # fmt: off
            if(len(tickers)!=1):
                ticker_df['Range', ticker] = ticker_df.High[ticker] - ticker_df.Low[ticker]
                ticker_df['RollingMax', ticker] = ticker_df.High[ticker].rolling(MAGIC_NUMBER).max()
                ticker_df['RollingMin', ticker] = ticker_df.Low[ticker].rolling(MAGIC_NUMBER).min()
                ticker_df['RollingRangeDivClose', ticker] = ((ticker_df.RollingMax[ticker] - ticker_df.RollingMin[ticker]) / ticker_df.Close[ticker])
                ticker_df['MinRetracement', ticker] = ticker_df.RollingRangeDivClose[ticker] * args.retracement_size
                ticker_df['MaxDiff', ticker] = ticker_df.RollingRangeDivClose[ticker] * args.dif
                # import pdbr; pdbr.set_trace()
                dfRes = createZigZagPoints(ticker_df.Close[ticker], ticker_df.MinRetracement[ticker]).dropna()
                candlestick2_ohlc(ax, ticker_df['Open'][ticker], ticker_df['High'][ticker], ticker_df['Low'][ticker], ticker_df['Close'][ticker], width=0.6, colorup='g', colordown='r')
                ax.set_ylim([ticker_df.Low[ticker].min()*0.95, ticker_df.High[ticker].max()*1.05])
                ax.set_xlim([MAGIC_NUMBER,ticker_df.index.max()])
                # axs[1].plot(ticker_df.MinRetracement[ticker])
            else:
                ax.set_ylim([ticker_df.Low.min()*0.95, ticker_df.High.max()*1.05])
                ax.set_xlim([MAGIC_NUMBER,ticker_df.index.max()])
                ticker_df['Range'] = ticker_df.High - ticker_df.Low
                ticker_df['RollingMax'] = ticker_df.High.rolling(MAGIC_NUMBER).max()
                ticker_df['RollingMin'] = ticker_df.Low.rolling(MAGIC_NUMBER).min()
                ticker_df['RollingRangeDivClose'] = ((ticker_df.RollingMax - ticker_df.RollingMin) / ticker_df.Close)
                ticker_df['MinRetracement'] = ticker_df.RollingRangeDivClose * args.retracement_size
                ticker_df['MaxDiff'] = ticker_df.RollingRangeDivClose * args.dif
                dfRes = createZigZagPoints(ticker_df.Close, ticker_df.MinRetracement).dropna()
                if not args.no_candle:
                    candlestick2_ohlc(ax, ticker_df["Open"], ticker_df["High"], ticker_df["Low"], ticker_df["Close"], width=0.5, colorup="g", colordown="r",)
                # axs[1].plot(ticker_df.MinRetracement)
            # fmt: on

            # print(dfRes)
            # axs[1].plot(ticker_df.Range)
            removed_indexes = []
            if args.target_max:
                has_line_near_target = False
            else:
                has_line_near_target = True

            # draw S/R lines
            lines = []
            if not args.no_sr_lines:
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
                            print("Support at ", end="")
                            for i in range(len(values) - 1):
                                if (
                                    args.target_max
                                    and values[i] < args.target_max
                                    and values[i] > args.target_min
                                ):
                                    has_line_near_target = True
                                print("{:0.2f} and ".format(values[i]), end="")
                            print("{:0.2f} \n".format(values[len(values) - 1]), end="")
                            removed_indexes.extend(dropindexes)
                            for value in values:
                                sum = sum + value
                            if endx > x_max:
                                x_max = endx
                            lines.append([startx, endx, sum / len(values)])
                            if not args.draw_boxes:
                                ax.hlines(
                                    y=sum / len(values),
                                    xmin=startx,
                                    xmax=endx,
                                    linewidth=1,
                                    color="w",
                                )

            if args.draw_boxes:
                from matplotlib.patches import Rectangle
                counter = 0
                for line in lines:
                    # import pdbr; pdbr.set_trace()
                    print(counter, line)
                    counter2 = 0
                    for line2 in lines:
                        if counter == counter2:
                            counter2 += 1
                            continue
                        if line2[0] == line[0] and line2[2] == line[2]: continue
                        # show all lines where the startx is before this lines' stopx
                        if line[1] > line2[0] and line[0] < line2[1]:
                            print("overlapping lines", counter2)

                            min_x = min(line[0], line2[0])
                            min_y = min(line[2], line2[2])
                            max_x = max(line[1], line[1])
                            max_y = max(line[2], line2[2])
                            ax.add_patch(
                                Rectangle((min_x, min_y), max_x-min_x, max_y-min_y,
                                          facecolor = 'white',
                                          fill=True,)
                            )
                        counter2 += 1

                    counter += 1

            # ax.plot(dfRes["Value"])
            # axs[2].plot(ticker_df.MaxDiff[ticker])
            # ax.text(.5,.8,f'{ticker} magic:{MAGIC_NUMBER}\nRollingRangeDivClose\nMinRetracement\nMaxDiff', horizontalalignment='center', transform=ax.transAxes)

            if has_line_near_target:
                plt.axis('off')
                if args.optimize:
                    # plt.title(title)
                    if not os.path.exists(os.path.dirname(outfile)):
                        os.makedirs(os.path.dirname(outfile))
                    plt.savefig(outfile)
                else:
                    # plt.title(ticker)
                    plt.show()



            plt.clf()
            plt.cla()
            plt.close()
        except Exception as e:
            print(e)
            raise (e)


if args.no_sr_lines:
    difs = [11]
else:
    difs = range(5, 15)

if args.optimize:
    for dif in difs:
        for ret in range(9, 15):
            for num in [2]:
                # if dif < seg: continue
                args.retracement_size = ret
                args.dif = dif
                args.number = num
                run(args)
else:
    run(args)
