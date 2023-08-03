import requests
import pandas as pd 
import os
import glob
import json
import plotly.graph_objects as go
from plotly.subplots import make_subplots

url = 'https://stablecoins.llama.fi/stablecoincharts/Ethereum?stablecoin=1'
asset_list = ['BUSD', 'DAI', 'FRAX', 'LUSD', 'MIM', 'MIMATIC', 'stETH', 'TUSD', 'USDC', 'USDD', 'USDT', 'VST', 'WBTC']
asset_drop = ['USDTz', 'DAI+', 'USDT+', 'ALUSD']
response = requests.get(url).json()
df = pd.DataFrame(response)

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

    fig.show()

def get_stablecoin_data():
    url = 'https://stablecoins.llama.fi/stablecoins?includePrices=true' 
    response = requests.get(url).json()['peggedAssets']
    df = pd.DataFrame(response)
    df = df[df['symbol'].isin(asset_list)]
    df = df[~df['symbol'].isin(asset_drop)]
    df_ids = df[['id', 'symbol', 'chains']]
    return df_ids

def get_chain_data(stablecoin_id, chain):
    url = f'https://stablecoins.llama.fi/stablecoincharts/{chain}?stablecoin={stablecoin_id}'
    response = requests.get(url).json()
    df = pd.DataFrame(response)
    return df

def main():
    df_ids = get_stablecoin_data()

    for index, row in df_ids.iterrows():
        stablecoin_id = row['id']
        stablecoin_symbol = row['symbol']
        chains = row['chains']
        for chain in chains:
            df_chain = get_chain_data(stablecoin_id, chain)
            
            # Create directory if it doesn't exist
            dir_path = os.path.join("data", stablecoin_symbol)
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
            
            # Save data in the created directory
            filename = os.path.join(dir_path, f"{chain}_data.csv")
            df_chain.to_csv(filename, index=False)

    # Loop over the asset list and plot the data
    for asset in asset_list:
        plot_token_data(asset)

if __name__ == '__main__':
    main()
