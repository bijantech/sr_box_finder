import pandas as pd
from pandas_datareader import data as pdr
import numpy as np
from os.path import exists
import os.path
import pathlib
import os
parent = pathlib.Path(__file__).parent.resolve()

symbols = ["AAPL", "MSFT", "GOOGL"]
# for symbol in symbols:
#     download(symbol)

def download(symbol):
    path_to_file = os.path.join(parent, f'../data/{symbol}.csv')
    if exists(path_to_file):
        print("already have data for", symbol)
        return
    print("downloading", path_to_file)
    start = "1980-01-01"
    end = "2022-06-15"
    ohlc = pdr.get_data_yahoo(symbol, start, end)
    ohlc.to_csv(path_to_file)

def load_data(symbol):
    path_to_file = os.path.join(parent, f'../data/{symbol}.csv')
    if not exists(path_to_file): download(symbol)
    ohlc = pd.read_csv(path_to_file, header=[0])
    ohlc.columns = ohlc.columns.droplevel(1)
    ohlc.index = pd.to_datetime(ohlc.index)
    return ohlc.copy()
    # return ohlc.reset_index()[['Date', 'Open', 'High', 'Low', 'Close', 'Volume']]
