import plotly
import plotly.graph_objs as go

data = [go.Scatter(x=[1,2,3,4], y=[1,2,4,3])]

plotly.offline.iplot(data)
