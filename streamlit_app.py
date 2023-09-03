import streamlit as st
import requests
import pandas as pd
import altair as alt

def fetch_luno_minute_data():
    url = "https://ajax.luno.com/ajax/1/udf/history?symbol=XBTMYR&resolution=60&from=1692495226&to=1693679626&countback=329&currencyCode=XBTMYR"
    response = requests.get(url)
    
    if response.status_code != 200:
        st.error(f"Failed to fetch data from Luno. Status Code: {response.status_code}. Message: {response.text}")
        return None

    data = response.json()
    
    if 's' in data and data['s'] != 'ok':
        st.error(f"Failed to fetch data from Luno. Message: {data['s']}")
        return None
    
    # Convert timestamp to datetime format
    df = pd.DataFrame({
        'time': pd.to_datetime(data['t'], unit='s'),
        'close_XBTMYR': data['c']
    })
    
    # Adjust the time to GMT+8
    df['time'] = df['time'] + pd.Timedelta(hours=8)
    
    return df

def fetch_binance_minute_data():
    url = "https://data.binance.com/api/v3/uiKlines?symbol=BTCUSDT&interval=1m&limit=5000"
    response = requests.get(url)
    
    if response.status_code != 200:
        st.error(f"Failed to fetch data from Binance. Status Code: {response.status_code}. Message: {response.text}")
        return None
    
    data = response.json()
    
    df = pd.DataFrame(data, columns=['open_time', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])
    
    # Convert timestamp to GMT+8 date-time format
    df['open_time'] = pd.to_datetime(df['open_time'], unit='ms') + pd.Timedelta(hours=8)
    
    return df[['open_time', 'close']].rename(columns={'open_time': 'time', 'close': 'close_BTCUSDT'})

API_KEY = 'fa5a93fd89864b948ec42ca316a6646a'  # Replace with your API key from Exchange Rates API

def fetch_usd_to_myr_conversion_rate():
    url = f"https://open.er-api.com/v6/latest/USD"
    response = requests.get(url)
    
    if response.status_code != 200:
        st.error("Failed to fetch conversion rate from Exchange Rates API.")
        return 1.0  # Default conversion rate
    
    data = response.json()
    return data['rates']['MYR']

st.title('Luno XBTMYR and Binance BTCUSDT Data (Close Price)')

luno_df = fetch_luno_minute_data()
binance_df = fetch_binance_minute_data()

if luno_df is not None and binance_df is not None:
    conversion_rate = fetch_usd_to_myr_conversion_rate()
    binance_df['close_BTCUSDT'] = binance_df['close_BTCUSDT'].astype(float) * conversion_rate

    chart1 = alt.Chart(luno_df).mark_line(color='blue').encode(
        x='time:T',
        y='close_XBTMYR:Q',
        tooltip=['time', 'close_XBTMYR']
    ).properties(
        title='Luno XBTMYR Close Price',
        width=400
    )

    chart2 = alt.Chart(binance_df).mark_line(color='red').encode(
        x='time:T',
        y='close_BTCUSDT:Q',
        tooltip=['time', 'close_BTCUSDT']
    ).properties(
        title='Binance BTCUSDT (Converted to MYR) Close Price',
        width=400
    )

    # Display charts side by side
    col1, col2 = st.columns(2)
    col1.altair_chart(chart1)
    col2.altair_chart(chart2)

else:
    st.write("Failed to fetch and merge data.")
