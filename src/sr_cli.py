import pandas as pd
pd.core.common.is_list_like = pd.api.types.is_list_like
import pandas_datareader.data as web
import os.path
import os
from argparse import ArgumentParser
from PIL import Image
from utils import draw_chart, get_data, measure_error, get_error2, ALL_TICKERS, AAYUSH_TICKERS
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
    "--sector",
    type=str,
    required=False,
    help="Sectors symbols",
)
parser.add_argument(
    "--start-date",
    type=str,
    required=False,
    help="Start Date",
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
    "--color",
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

def run(args):
    if args.sector:
        df = read_sectors()
        tsyms = df[[args.sector]].dropna()[args.sector].str.split(":").str[-1].values
        tsyms = ",".join(list(tsyms[3:].astype(str)))
        args.tickers = tsyms

    if (args.tickers=="SPY500"):
        args.tickers = ALL_TICKERS
    elif (args.tickers=="AAYUSH"):
        args.tickers = AAYUSH_TICKERS
    else:
        args.tickers = args.tickers.split(",")
    print(args.tickers)
    ticker_df = get_data(args)

    if args.verbose:
        os.environ['SRCLI_VERBOSE'] = "1"
    else:
        os.environ['SRCLI_VERBOSE'] = ""

    for ticker in args.tickers:
        if args.show:
            print("\n"+ticker)
        args.ticker = ticker
        errors = []

        [sample, covered] = draw_chart(ticker_df, args, True)
        sampleimg = Image.open(sample).convert('RGB')

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
                        [outfile, covered] = draw_chart(ticker_df, args)
                        if os.path.exists(outfile):
                            new = Image.open(outfile).convert('RGB')
                            error = measure_error(sampleimg, new)
                            # print("err", error)
                            errors.append([ticker, dif, ret, num, outfile,
                                           error, covered])
                        # print("dif", dif, "ret", ret)
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

            [outfile, covered] = draw_chart(ticker_df, args)
            new = Image.open(outfile).convert('RGB')
            error = measure_error(sampleimg, new)

            if os.path.exists("data/output.csv"):
                df = pd.read_csv('data/output.csv')
            else:
                df = pd.DataFrame(errors, columns=['symbol', 'outfile', 'err', 'covered'])

            error = measure_error(sampleimg, new)
            errors.append([ticker, outfile, error, covered])
            df = df.drop(df[df.symbol == ticker].index)
            df1 = pd.DataFrame(errors, columns=['symbol', 'outfile', 'err', 'covered'])
            pd.concat([df1, df]).to_csv(f'data/output.csv', index=False)

if __name__ == "__main__":
    run(parser.parse_args())
