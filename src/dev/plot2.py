import matplotlib.pyplot as plt
from mpl_finance import candlestick_ohlc
import pandas as pd
import matplotlib.dates as mpl_dates

plt.style.use("ggplot")

# Extracting Data for plotting
data = pd.read_csv("BTCUSDT.csv")

ohlc = data.loc[:, ["date", "open", "high", "low", "close"]]
ohlc["date"] = pd.to_datetime(ohlc["date"])
ohlc["date"] = ohlc["date"].apply(mpl_dates.date2num)
ohlc = ohlc.astype(float)

# Creating Subplots
fig, ax = plt.subplots()

candlestick_ohlc(
    ax, ohlc.values, width=0.6, colorup="green", colordown="red", alpha=0.8
)

# Setting labels & titles
ax.set_xlabel("Date")
ax.set_ylabel("Price")
fig.suptitle("Daily Candlestick Chart of BTCUSDT")

# Formatting Date
date_format = mpl_dates.DateFormatter("%d-%m-%Y")
ax.xaxis.set_major_formatter(date_format)
fig.autofmt_xdate()

fig.tight_layout()

plt.show()
