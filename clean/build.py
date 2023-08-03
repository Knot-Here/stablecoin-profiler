import os
import glob
import json
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import requests

asset_list = ['BUSD', 'DAI', 'FRAX', 'LUSD', 'MIM', 'MAI', 'TUSD', 'USDC', 'USDD', 'USDT', 'VST']

url = 'https://stablecoins.llama.fi/stablecoins?includePrices=true' 

def get_all_files(symbol):
    all_files = glob.glob(f"data/{symbol}/*.csv")
    return all_files

def plot_token_data(symbol):
    all_files = get_all_files(symbol)
    df_list = []

    for file in all_files:
        df_temp = pd.read_csv(file)
        chain = os.path.basename(file).split('_')[0]  # get the chain name from the filename
        df_temp['chain'] = chain
        df_list.append(df_temp)

    df_merged = pd.concat(df_list, ignore_index=True)

    df_merged['date'] = pd.to_datetime(df_merged['date'], unit='s')  # convert timestamp to datetime
    df_merged.set_index('date', inplace=True)  # set date as index

    df_merged['totalCirculatingUSD'] = df_merged['totalCirculating'].apply(lambda x: json.loads(x.replace("'", "\""))['peggedUSD'])  # extract totalCirculatingUSD

    chains = df_merged['chain'].unique()

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.layout.template = 'plotly_dark'

    for chain in chains:
        df_chain = df_merged[df_merged['chain'] == chain]
        fig.add_trace(go.Scatter(x=df_chain.index, y=df_chain['totalCirculatingUSD'], name=chain))

    fig.update_layout(title=f'Total circulating USD value of {symbol} over different chains over time',
                      xaxis_title='Date',
                      yaxis_title='Total circulating USD value')

    fig.write_html(f"charts/{symbol}_chain.html")


def get_stablecoin_data():
    response = requests.get(url).json()['peggedAssets']
    df = pd.DataFrame(response)
    df_ids = df[['id', 'symbol']]
    return df_ids

def stablecoin_data(id_, TICKER):
    url = f'https://stablecoins.llama.fi/stablecoincharts/all?stablecoin={id_}'
    response = requests.get(url).json()
    df = pd.DataFrame(response)
    df['date'] = pd.to_datetime(df['date'], unit='s')

    for col in df.columns[1:]:
        df[col] = df[col].apply(lambda x: x['peggedUSD'])

    fig = make_subplots(specs=[[{'type': 'scatter'}]])
    fig.layout.template = 'plotly_dark'

    for col in df.columns[1:]:
        fig.add_trace(go.Scatter(x=df['date'], y=df[col], mode='lines', name=col))

    fig.update_layout(title=f"{TICKER} Circulation, Mint, and Bridge Data",
                      xaxis_title="Date",
                      yaxis_title="Value in USD",
                      font=dict(size=12, color="white", family="Courier New, monospace"))

    fig.write_html(f"charts/{TICKER}_data.html")


def main():
    # Create the charts directory if it does not exist
    if not os.path.exists("charts"):
        os.makedirs("charts")

    # Loop over the asset list and plot the data
    for asset in asset_list:
        plot_token_data(asset)

    df_ids = get_stablecoin_data()
    for index, row in df_ids.iterrows():
        stablecoin_id = row['id']
        stablecoin_symbol = row['symbol']
        stablecoin_data(stablecoin_id, stablecoin_symbol)

    with open('index.html', 'w') as f:
        f.write("<html>\n")
        f.write("<body>\n")
        f.write("<link rel='stylesheet' type='text/css' href='styles.css'>")
        f.write("<h1>Stablecoin Plots</h1>\n")
        for asset in asset_list:
            f.write(f'<p><a href="charts/{asset}_chain.html">{asset} Chain Data</a></p>\n')
            f.write(f'<p><a href="charts/{asset}_data.html">{asset} Data</a></p>\n')
        f.write("</body>\n")
        f.write("</html>\n")

if __name__ == '__main__':
    main()
