import plotly.graph_objects as go
import pandas as pd
from ta.trend import MACD
from ta.momentum import StochasticOscillator
import cufflinks as cf

cf.set_config_file(theme='pearl',sharing='public',offline=True)

df = pd.read_csv('BTCUSDT.csv').set_index('date')

macd = MACD(close=df['close'],
            window_slow=26,
            window_fast=12,
            window_sign=9)

stoch = StochasticOscillator(high=df['high'],
                             close=df['close'],
                             low=df['low'],
                             window=14,
                             smooth_window=3)



print(df.columns)

df['MA20'] = df['close'].rolling(window=20).mean()
df['MA5'] = df['close'].rolling(window=5).mean()

fig = go.Figure()

fig.add_trace(go.Candlestick(x=df.index,
                             open=df['open'],
                             high=df['high'],
                             low=df['low'],
                             close=df['close'],
                             showlegend=False))

fig.add_trace(go.Scatter(x=df.index,
                         y=df['MA5'],
                         opacity=0.7,
                         line=dict(color='blue', width=2),
                         name='MA 5'))
fig.add_trace(go.Scatter(x=df.index,
                         y=df['MA20'],
                         opacity=0.7,
                         line=dict(color='orange', width=2),
                         name='MA 20'))

fig.show()
