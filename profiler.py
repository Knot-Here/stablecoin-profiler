import requests
import pandas as pd

asset_list = ['BUSD', 'DAI', 'FRAX', 'LUSD', 'MIM', 'MAI', 'stETH', 'TUSD', 'USDC', 'USDD', 'USDT', 'VST', 'WBTC']
asset_drop = ['USDTz', 'DAI+', 'USDT+', 'ALUSD']
column_drop = ['gecko_id', 'priceSource', 'delisted', 'chains', 'chainCirculating']

url = 'https://stablecoins.llama.fi/stablecoins?includePrices=true'
res = requests.get(url).json()
df = pd.DataFrame(res['peggedAssets'])
df = df[df['symbol'].isin(asset_list)]
df = df[~df['symbol'].isin(asset_drop)]
df = df.drop(columns=column_drop)
df['circulating'] = df['circulating'].apply(lambda x: x['peggedUSD'])
df['circulatingPrevDay'] = df['circulatingPrevDay'].apply(lambda x: x['peggedUSD'])
df['circulatingPrevWeek'] = df['circulatingPrevWeek'].apply(lambda x: x['peggedUSD'])
df['circulatingPrevMonth'] = df['circulatingPrevMonth'].apply(lambda x: x['peggedUSD'])

data_list = []

for i in df['id'].to_list():
    url = 'https://stablecoins.llama.fi/stablecoin/' + i
    res = requests.get(url).json()
    data = {
        'name': res['name'],
        'symbol': res['symbol'],
        'url': res['url'],
        'description': res['description'],
        'mintRedeemDescription': res['mintRedeemDescription']
    }
    data_list.append(data)

# Convert the data list to a DataFrame
additional_df = pd.DataFrame(data_list)

# Concatenate the additional DataFrame with the existing DataFrame
df = pd.concat([df, additional_df], axis=1)

# Drop rows with NaN in the 'id' column
df = df.dropna(subset=['id'])

# Generate an HTML table from the DataFrame
table_html = df.to_html(index=False, float_format='%.3f')

# Load the HTML template file and insert the generated table HTML
with open('temp_index.html', 'r') as file:
    html_template = file.read()

# Replace the placeholder for the table with the generated HTML table
final_html = html_template.replace('{{table_html}}', table_html)

# Save the final HTML file with the table included
with open('index.html', 'w') as file:
    file.write(final_html)