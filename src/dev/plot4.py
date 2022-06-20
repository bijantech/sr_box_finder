import mplfinance as mpf
import pandas as pd

# import matplotlib.pyplot as plt
# from mplfinance import candlestick_ohlc
# import pandas as pd
import matplotlib.dates as mpl_dates

#
# plt.style.use('ggplot')

# Extracting Data for plotting
data = pd.read_csv("BTCUSDT.csv")

ohlc = data.loc[:, ["date", "open", "high", "low", "close"]]
ohlc["date"] = pd.to_datetime(ohlc["date"])
# ohlc['date'] = ohlc['date'].apply(mpl_dates.date2num)
# ohlc = ohlc.astype(float)
ohlc.set_index("date", inplace=True)

mpf.plot(ohlc, type="candle", mav=(3, 6, 9))
