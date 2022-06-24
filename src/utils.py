import pandas as pd
from platform import system

pd.core.common.is_list_like = pd.api.types.is_list_like
import pandas_datareader.data as web
import datetime
import yfinance as yahoo_finance
yahoo_finance.pdr_override()
from pandas_datareader.yahoo.headers import DEFAULT_HEADERS
import requests_cache
import os
from mathutil import overlap

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

def get_data(args):
    ticker_df = web.get_data_yahoo(
        args.tickers, period=args.period, interval=args.interval, session=session
    )
    ticker_df.index = pd.to_datetime(ticker_df.index)
    if args.start_date:
        ticker_df = ticker_df[args.start_date :]
    if args.stop_date:
        ticker_df = ticker_df[: args.stop_date]
    return ticker_df.reset_index()

def log(*argv, **kwargs):
    if os.environ['SRCLI_VERBOSE']:
        print(*argv, **kwargs)

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
