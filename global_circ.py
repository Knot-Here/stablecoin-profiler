import requests
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio

url = 'https://stablecoins.llama.fi/stablecoins?includePrices=true' 

asset_list = ['BUSD', 'DAI', 'FRAX', 'LUSD', 'MIM', 'MAI', 'stETH', 'TUSD', 'USDC', 'USDD', 'USDT', 'VST', 'WBTC']
asset_drop = ['USDTz', 'DAI+', 'USDT+', 'ALUSD']

def get_stablecoin_data():
    response = requests.get(url).json()['peggedAssets']
    df = pd.DataFrame(response)
    df = df[df['symbol'].isin(asset_list)]
    df = df[~df['symbol'].isin(asset_drop)]
    return df[['id', 'symbol']]

def get_stablecoin_history(id_):
    url = f'https://stablecoins.llama.fi/stablecoincharts/all?stablecoin={id_}'
    response = requests.get(url).json()
    df = pd.DataFrame(response)
    df['date'] = pd.to_datetime(df['date'], unit='s')
    df['totalCirculating'] = df['totalCirculating'].apply(lambda x: x['peggedUSD'])
    return df[['date', 'totalCirculating']]

def main():
    df_ids = get_stablecoin_data()
    fig = go.Figure()

    for index, row in df_ids.iterrows():
        stablecoin_id = row['id']
        stablecoin_symbol = row['symbol']
        df_history = get_stablecoin_history(stablecoin_id)
        fig.add_trace(go.Scatter(x=df_history['date'], y=df_history['totalCirculating'],
                                 mode='lines',
                                 name=stablecoin_symbol))

    # Use the plotly_dark template for a dark-themed plot
    pio.templates.default = "plotly_dark"

    fig.update_layout(
        title="Historical Total Circulation of Each Stablecoin",
        xaxis_title="Date",
        yaxis_title="Total Circulation (USD)",
        font=dict(
            size=12,
            color="white",
            family="Courier New, monospace"
        )
    )
    fig.layout.template = 'plotly_dark'
    fig.write_html("charts/total_circulation_history.html")

if __name__ == '__main__':
    main()
