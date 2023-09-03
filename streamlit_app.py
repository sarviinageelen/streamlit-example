import streamlit as st
import requests
import pandas as pd

def fetch_luno_minute_data():
    url = "https://ajax.luno.com/ajax/1/udf/history?symbol=XBTMYR&resolution=60&from=1692495226&to=1693679626&countback=329&currencyCode=XBTMYR"
    response = requests.get(url)
    
    if response.status_code != 200 or 's' in response.json() and response.json()['s'] != 'ok':
        st.error("Failed to fetch data from Luno.")
        return None
    
    data = response.json()
    
    # Convert timestamp to datetime format
    df = pd.DataFrame({
        'time': pd.to_datetime(data['t'], unit='s'),
        'close_XBTMYR': data['c']
    })
    
    # Adjust the time to GMT+8
    df['time'] = df['time'] + pd.Timedelta(hours=8)
    
    return df

def fetch_binance_minute_data():
    url = "https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=1m&limit=500"
    response = requests.get(url)
    
    if response.status_code != 200:
        st.error("Failed to fetch data from Binance.")
        return None
    
    data = response.json()
    
    df = pd.DataFrame(data, columns=['open_time', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])
    
    # Convert timestamp to GMT+8 date-time format
    df['open_time'] = pd.to_datetime(df['open_time'], unit='ms') + pd.Timedelta(hours=8)
    
    return df[['open_time', 'close']].rename(columns={'open_time': 'time', 'close': 'close_BTCUSDT'})

st.title('Luno XBTMYR and Binance BTCUSDT Data (Close Price)')

luno_df = fetch_luno_minute_data()
binance_df = fetch_binance_minute_data()

if luno_df is not None and binance_df is not None:
    merged_df = pd.merge_asof(luno_df, binance_df, on='time', direction='nearest').set_index('time')
    st.write(merged_df)
    st.line_chart(merged_df)
