import plotly.graph_objects as go
from plotly.subplots import make_subplots
import yfinance as yf
import main

#returns volume and closing price data for past month
def getVolPriceData(ticker):
    with main.suppress_stdout():
        data = yf.Ticker(ticker).history(period = '3mo')[['Volume', 'Close']]
    data['Date'] = data.index
    return data

#plots volume (bar-chart) and closing price (scatter)
def plotVolPrice(volPriceData, ticker):
    date = volPriceData['Date'].tolist()
    vol = volPriceData['Volume'].tolist()
    price = volPriceData['Close'].tolist()
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(
    go.Bar(x=date, y=vol, name="Volume"),
        secondary_y=False,)
    fig.add_trace(
    go.Scatter(x=date, y=price, name="Closing Price"),
    secondary_y=True,)

    fig.update_layout(
    title_text="Past 3-Month Closing Price and Volume for " + ticker)

    fig.update_xaxes(title_text="date")

    fig.update_yaxes(title_text="Shares Traded", secondary_y=False)
    fig.update_yaxes(title_text="Closing Stock Price", secondary_y=True)
    fig.show()

#controls plotting ui
def plotUI(ticker_bucket):
    print("********VOLUME PLOTTING MODULE********")
    print("View 3-month volume and closing price \ndata for a stock")
    print("Type 'watchlist' to see detected list")
    print("-" * 38)
    while True:
        ticker = input("Enter ticker (type back to return to main menu): ")
        if ticker == "watchlist":
            print(ticker_bucket)
            continue
        ticker = ticker.upper().replace(" ", "")
        if ticker == "BACK":
            break
        data = getVolPriceData(ticker)
        if data.empty:
            print("Ticker data not available.")
            continue
        plotVolPrice(data, ticker)
