import requests
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
from plotly.subplots import make_subplots
import os
import base64

url = 'https://stablecoins.llama.fi/stablecoins?includePrices=true' 

asset_list = ['BUSD', 'DAI', 'FRAX', 'LUSD', 'MIM', 'MAI', 'stETH', 'TUSD', 'USDC', 'USDD', 'USDT', 'VST', 'WBTC']
asset_drop = ['USDTz', 'DAI+', 'USDT+', 'ALUSD']
column_drop = ['gecko_id', 'priceSource']

# with open("y2k.png", "rb") as image_file:
#     encoded_string = base64.b64encode(image_file.read()).decode()

def get_stablecoin_data():
    response = requests.get(url).json()['peggedAssets']
    df = pd.DataFrame(response)
    df = df[df['symbol'].isin(asset_list)]
    df = df[~df['symbol'].isin(asset_drop)]
    df_ids = df[['id', 'symbol']]
    return df_ids

def stablecoin_data(id_, TICKER, filename):
    url = f'https://stablecoins.llama.fi/stablecoincharts/all?stablecoin={id_}'
    response = requests.get(url).json()
    df = pd.DataFrame(response)
    df['date'] = pd.to_datetime(df['date'], unit='s')

    for col in df.columns[1:]:
        df[col] = df[col].apply(lambda x: x['peggedUSD'])

    # Create a plot
    pio.templates.default = "plotly_dark"
    fig = make_subplots(
        rows=1, cols=1,
        subplot_titles=(TICKER,),
        specs=[[{'type': 'scatter'}]],
        horizontal_spacing=0.03,
        vertical_spacing=0.1,
    )

    # Add traces for each column
    for col in df.columns[1:]:
        fig.add_trace(go.Scatter(x=df['date'], y=df[col],
                                 mode='lines',
                                 name=col))

    fig.update_layout(
        title=f"{TICKER} Circulation, Mint, and Bridge Data",
        xaxis_title="Date",
        yaxis_title="Value in USD",
        font=dict(
            size=12,
            color="white",
            family="Courier New, monospace"
        )
    )

    # Save the figure as html
    fig.write_html(filename)
    with open(filename, 'a') as f:
        f.write('<br><a href="../../../index.html">Go back to the list</a>')


def main():
    df_ids = get_stablecoin_data()

    for index, row in df_ids.iterrows():
        stablecoin_id = row['id']
        stablecoin_symbol = row['symbol']
        filename = os.path.join("charts/global", f"{stablecoin_symbol}_data.html")
        stablecoin_data(stablecoin_id, stablecoin_symbol, filename)

if __name__ == '__main__':
    main()
