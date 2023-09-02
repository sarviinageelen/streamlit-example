import streamlit as st
import requests
import pandas as pd
import datetime

def fetch_binance_minute_data():
    base_url = "https://api.binance.com/api/v3/klines"
    symbol = "BTCUSDT"
    interval = "1m"
    limit = 1000  # fetch maximum of 1000 data points
    
    params = {
        "symbol": symbol,
        "interval": interval,
        "limit": limit
    }
    
    response = requests.get(base_url, params=params)
    
    if response.status_code != 200:
        st.error("Failed to fetch data from Binance.")
        return None
    
    data = response.json()
    df = pd.DataFrame(data, columns=['open_time', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])
    df['open_time'] = pd.to_datetime(df['open_time'], unit='ms')
    df['close_time'] = pd.to_datetime(df['close_time'], unit='ms')
    
    return df[['open_time', 'open', 'high', 'low', 'close', 'volume']]

st.title('Binance BTCUSDT Minute Data')

df = fetch_binance_minute_data()

if df is not None:
    st.write(df)
    st.line_chart(df[['open', 'high', 'low', 'close']])
