import plotly.graph_objects as go
import pandas as pd

df = pd.read_csv(
    "https://raw.githubusercontent.com/plotly/datasets/master/finance-charts-apple.csv"
)

print(df.columns)
df["MA20"] = df["Close"].rolling(window=20).mean()
df["MA5"] = df["Close"].rolling(window=5).mean()

fig = go.Figure(
    data=go.Ohlc(
        x=df["Date"],
        open=df["AAPL.Open"],
        high=df["AAPL.High"],
        low=df["AAPL.Low"],
        close=df["AAPL.Close"],
    )
)
fig.show()
