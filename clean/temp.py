import requests
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio

# BLOCKCHAIN STABLECOIN MARKETSHARES
def chain_stable_share():
    url = 'https://stablecoins.llama.fi/stablecoinchains'
    response = requests.get(url).json()
    df = pd.DataFrame(response)
    return df


def stablecoin_data(TICKER):
    url = 'https://stablecoins.llama.fi/stablecoincharts/all?stablecoin=7'
    response = requests.get(url).json()
    df = pd.DataFrame(response)
    print(df)
    df['date'] = pd.to_datetime(df['date'], unit='s')

    for col in df.columns[1:]:
        df[col] = df[col].apply(lambda x: x['peggedUSD'])

    # Create a plot
    pio.templates.default = "plotly_dark"
    fig = go.Figure()

    # Add traces for each column
    for col in df.columns[1:]:
        fig.add_trace(go.Scatter(x=df['date'], y=df[col],
                        mode='lines',
                        name=col))

    fig.update_layout(
        title="Stablecoin Data",
        xaxis_title="Date",
        yaxis_title="Value in USD",
        font=dict(
            size=12,
            color="white"
        ),
    )

    # Save the figure as html
    fig.write_html("stablecoin_data.html")