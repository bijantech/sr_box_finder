import trendln
# this will serve as an example for security or index closing prices, or low and high prices
import yfinance as yf # requires yfinance - pip install yfinance
tick = yf.Ticker('^GSPC') # S&P500
hist = tick.history(period="max", rounding=True)
h = hist[-1000:].Close
mins, maxs = trendln.calc_support_resistance(h, accuracy=8)
minimaIdxs, pmin, mintrend, minwindows = trendln.calc_support_resistance((hist[-1000:].Low, None), accuracy=8) #support only
mins, maxs = trendln.calc_support_resistance((hist[-1000:].Low,
                                              hist[-1000:].High), accuracy=8)
(minimaIdxs, pmin, mintrend, minwindows), (maximaIdxs, pmax, maxtrend, maxwindows) = mins, maxs
