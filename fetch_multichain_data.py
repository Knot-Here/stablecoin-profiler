import requests
import pandas as pd 
import os

url = 'https://stablecoins.llama.fi/stablecoincharts/Ethereum?stablecoin=1'
asset_list = ['BUSD', 'DAI', 'FRAX', 'LUSD', 'MIM', 'stETH', 'TUSD', 'USDC', 'USDD', 'USDT', 'VST', 'WBTC']
asset_list = ['STETH']
asset_drop = ['USDTz', 'DAI+', 'USDT+', 'ALUSD']
response = requests.get(url).json()
df = pd.DataFrame(response)

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

if __name__ == '__main__':
    main()
