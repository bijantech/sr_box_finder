from pandas_datareader import data as pdr
import matplotlib.pyplot as plt
import pandas as pd
from mpl_finance import candlestick_ohlc
import numpy as np


def calc_slope(x):
    slope = np.polyfit(range(len(x)), x, 1)[0]
    return slope


plt.style.use("ggplot")

start = "2018-01-01"
end = "2022-06-15"
symbols = ["ROKU"]
# ohlc = pdr.get_data_yahoo(symbols, start, end)
ohlc = pd.read_csv("data/roku.csv", header=[0, 1], index_col=[0])
ohlc.index = pd.to_datetime(ohlc.index)

ohlc["avg"] = ohlc["Close"].rolling(window=50).mean()
ohlc["slope"] = ohlc["Close"].rolling(100, min_periods=2).apply(calc_slope)

fig, axs = plt.subplots(3, sharex=True, sharey=False, figsize=(12, 10))

axs[0].plot(ohlc["Close"])
axs[0].plot(ohlc["Close"].rolling(window=50).mean())

axs[1].plot(
    ohlc["Close"].rolling(100, min_periods=2).apply(calc_slope),
    label="9-Day ROC",
    color="blue",
)
axs[2].plot(
    ohlc["Close"].rolling(200, min_periods=2).apply(calc_slope),
    label="9-Day ROC",
    color="black",
)

plt.show()
