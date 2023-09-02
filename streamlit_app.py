import streamlit as st
import requests
import pandas as pd
import pytz

def fetch_luno_minute_data():
    url = "https://ajax.luno.com/ajax/1/udf/history?symbol=XBTMYR&resolution=60&from=1692495226&to=1693679626&countback=329&currencyCode=XBTMYR"
    response = requests.get(url)
    
    if response.status_code != 200 or 's' in response.json() and response.json()['s'] != 'ok':
        st.error("Failed to fetch data from Luno.")
        return None
    
    data = response.json()
    
    # Convert timestamp to GMT+8 date-time format
    df = pd.DataFrame({
        'time': pd.to_datetime(data['t'], unit='s').dt.tz_localize('UTC').dt.tz_convert('Asia/Kuala_Lumpur'),
        'close': data['c']
    })
    
    return df

st.title('Luno XBTMYR Data (Close Price)')

df = fetch_luno_minute_data()

if df is not None:
    st.write(df)
    st.line_chart(df.set_index('time'))
