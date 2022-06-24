import pandas as pd
pd.core.common.is_list_like = pd.api.types.is_list_like
import pandas_datareader.data as web
import os.path
import os
from argparse import ArgumentParser
from PIL import Image
from utils import get_data, ALL_TICKERS, AAYUSH_TICKERS
from chart import Chart
from tqdm.auto import tqdm
from sectors import read_sectors

parser = ArgumentParser(description="Algorithmic Support and Resistance")
parser.add_argument(
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
    default="7",
    type=float,
    required=False,
    help="Max %% difference between two points to group them together. Default: 10",
)
parser.add_argument(
    "-r",
    "--retracement-size",
    default="5",
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
    "--sectors",
    type=str,
    required=False,
    help="Sectors symbols",
)
parser.add_argument(
    "--start-date",
    type=str,
    default="2021-11-01",
    required=False,
    help="Start Date",
)
parser.add_argument(
    "--stop-date",
    type=str,
    required=False,
    default="2022-06-18",
    help="Stop Date",
)
parser.add_argument(
    "--optimize",
    action="store_true",
    required=False,
    help="Run many variables and save file (wont display)",
)
parser.add_argument(
    "--show-candles",
    action="store_true",
    required=False,
    help="Show candlesticks",
)
parser.add_argument(
    "--no-sr-lines",
    action="store_true",
    required=False,
    help="Dont show s/r lines",
)
parser.add_argument(
    "--no-boxes",
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
parser.add_argument(
    "--sample-only",
    action="store_true",
    required=False,
    help="Draw sample only",
)
parser.add_argument(
    "--show-zags",
    action="store_true",
    required=False,
    help="Show zig zags",
)
parser.add_argument(
    "--is-in-box",
    action="store_true",
    required=False,
    help="Show zig zags",
)
parser.add_argument(
    "--filter",
    action="store_true",
    required=False,
    help="Run Filter",
)
parser.add_argument(
    "--side-by-side",
    action="store_true",
    required=False,
    help="Show sample on right",
)
parser.add_argument(
    "--colors",
    action="store_true",
    required=False,
    help="Show multiple colors for boxes",
)
parser.add_argument(
    "--show",
    action="store_true",
    required=False,
    help="Show multiple colors for boxes",
)
parser.add_argument(
    "--cli",
    action="store_true",
    required=False,
    help="Know when run from cli to show applicable logs",
)

def run(args):
    if (args.sectors=="ALL"):
        sectors = read_sectors(None).columns
    elif args.sectors is not None:
        sectors = args.sectors.split(",")
        # sectors = [args.sectors]
    else:
        sectors = [None]

    for sector in sectors:
        args.sectors = sector
        if args.sectors:
            args.tickers = read_sectors(sector)
            if len(args.tickers) == 0:
                print(f"{sector} sector has no tickers!")
                continue
            else:
                print("Running", args.sectors)

        if (args.tickers=="SPY500"):
            args.tickers = ALL_TICKERS
        elif (args.tickers=="AAYUSH"):
            args.tickers = AAYUSH_TICKERS
        else:
            args.tickers = args.tickers.split(",")
        # print(args.tickers)
        ticker_df = get_data(args)

        if args.verbose:
            os.environ['SRCLI_VERBOSE'] = "1"
        else:
            os.environ['SRCLI_VERBOSE'] = ""

        for ticker in args.tickers:
            try:
                if args.show:
                    print("\n"+ticker)
                args.ticker = ticker
                errors = []

                chart = Chart(ticker_df, args, True)

                if args.optimize:
                    total_count = len(args.diffs) * len(args.rets)
                    pbar = tqdm(total = total_count)
                    counter = 0
                    for dif in args.diffs:
                        for ret in args.rets:
                            for num in args.nums:
                                # if dif < seg: continue
                                args.retracement_size = ret
                                args.dif = dif
                                args.number = num
                                chart = Chart(ticker_df, args)
                                if os.path.exists(chart.outfile):
                                    errors.append([
                                        chart.ticker,
                                        chart.dif,
                                        chart.ret,
                                        chart.num,
                                        chart.outfile,
                                        chart.error,
                                        chart.covered])
                                pbar.update(1)
                                counter += 1

                    pbar.close()
                    df = pd.read_csv('data/samples.csv')
                    df = df.drop(df[df.symbol == ticker].index)
                    df1 = pd.DataFrame(errors, columns=['symbol', 'dif','ret','num',
                                                        'outfile', 'err', 'covered'])
                    pd.concat([df1, df]).to_csv(f'data/samples.csv', index=False)
                else:
                    if args.sample_only: return
                    chart = Chart(ticker_df, args)
                    cols = ['sector', 'symbol', 'outfile', 'err', 'covered',
                            'boxes', 'lastprice', 'price_in_box']
                    if os.path.exists("data/output.csv"):
                        df = pd.read_csv('data/output.csv')
                    else:
                        df = pd.DataFrame(errors, columns=cols)

                    errors.append([
                        sector,
                        chart.ticker,
                        chart.outfile,
                        chart.error,
                        chart.covered,
                        chart.boxes,
                        chart.last_price,
                        chart.price_in_box,
                    ])
                    if args.cli: print(chart)
                    df = df.drop(df[df.symbol == ticker].index)
                    df1 = pd.DataFrame(errors, columns=cols)
                    pd.concat([df1, df]).to_csv(f'data/output.csv', index=False)
            except Exception as e:
                print("Run failed:", ticker, e)
                raise(e)

if __name__ == "__main__":
    args = parser.parse_args()
    args.cli = True
    run(args)
