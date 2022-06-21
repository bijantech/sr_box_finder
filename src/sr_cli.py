import pandas as pd
pd.core.common.is_list_like = pd.api.types.is_list_like
import pandas_datareader.data as web
import os.path
import os
import yfinance as yahoo_finance
yahoo_finance.pdr_override()
from argparse import ArgumentParser
from PIL import Image
from utils import draw_chart, get_data, measure_error

SOURCE_LINES= {
    "UPWK": [[132,158,16], [132,158,19.95],], #--start-date=2021-11-01 --stop-date=2022-06-18
    "ARKK": [[57,66,68.5], [63,70,77],
             [81,106,71.37], [91,120,52.25],
             [133,155,36.0],[145,151,46.02],] #--start-date=2021-11-01 --stop-date=2022-06-18
}

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
        args.ticker = ticker
        ticker_df = get_data(args)
        errors = []

        sample = Image.open(draw_chart(ticker_df, args, SOURCE_LINES[ticker])).convert('RGB')

        if args.optimize:
            for dif in difs:
                for ret in range(9, 15):
                    for num in [2]:
                        # if dif < seg: continue
                        args.retracement_size = ret
                        args.dif = dif
                        args.number = num
                        outfile = draw_chart(ticker_df, args)
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
            draw_chart(ticker_df, args)
