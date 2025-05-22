import streamlit as st
import pandas as pd



username=st.session_state.get('username')
DATA_FILE = f"data/data_{username}.csv"



# 读取/保存数据函数
def load_data():
    return pd.read_csv(DATA_FILE, parse_dates=["date"])

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

dataframe= load_data()

st.write(dataframe)