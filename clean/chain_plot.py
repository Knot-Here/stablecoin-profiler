import glob
import pandas as pd
import json
import os
import plotly.graph_objects as go
from plotly.subplots import make_subplots

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
    fig.write_html(f"charts/chains/{symbol}.html")


plot_token_data('MAI')
