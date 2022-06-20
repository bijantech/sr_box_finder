from pandas_datareader import data as pdr
import matplotlib.pyplot as plt
import pandas as pd

plt.style.use("ggplot")

# # Display
plt.figure(figsize=(20, 10))
plt.title("Opening Prices from {} to {}".format(start, end))
plt.plot(data["Close"])
plt.show()
