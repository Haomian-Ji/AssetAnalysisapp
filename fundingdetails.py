import streamlit as st
import pandas as pd



username=st.session_state.get('username')
DATA_FILE = f"data/data_{username}.csv"



# 读取/保存数据函数
def load_data():
    return pd.read_csv(DATA_FILE, parse_dates=["date"])

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

df= load_data()

# selected = df.loc[dataframe['money']>0]
# 删除缺失值
df_dropped = df.dropna()        # 删除包含缺失值的行

# 删除列
df_dropped = df_dropped.drop(columns=["stocks","option","efts"])

st.write(df_dropped)