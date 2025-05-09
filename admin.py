import streamlit as st
import streamlit_authenticator as stauth

import yaml
from yaml.loader import SafeLoader
from streamlit_authenticator.utilities import *

import csv
import datetime
import os
import pandas as pd

# 打开用户文件
with open('data/config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

users = config['credentials']['usernames']
for key in users:
    username=key
    st.write(key)



# 自定义文件名（带日期示例）
# default_filename = f"data_{selected_date.strftime('%Y%m%d')}.csv"

default_filename = f"data/data_{username}.csv"
filename = st.text_input("保存文件名", value=default_filename)

# # 初始化数据文件
if not os.path.exists(filename):
    pd.DataFrame(columns=["date", "totalAssets", "cash","stocks","option","efts",
                                 "cumulative","netAssets","dailyReturns"]).to_csv(filename, index=False)



with st.form("multi_field_form"):
        # 日期选择组件（默认今天）
    selected_date = st.date_input("选择日期", value=datetime.datetime.now())

    totalAssets = st.text_input("总资产")
    cash = st.text_input("现金")
    stocks = st.text_input("股票")
    option = st.text_input("期权")
    efts = st.text_input("EFTs")

    # 累计收益
    cumulative = st.text_input("累计收益")
    # 净资产
    netAssets = st.text_input("净资产")
    # 当日收益
    dailyReturns = st.text_input("当日收益")



    submitted = st.form_submit_button("提交")
    
    if submitted:
        if totalAssets and cash and stocks and option and efts :
            with open(filename, "a") as f:
                writer = csv.writer(f)
                writer.writerow([selected_date,
                                 totalAssets, cash,stocks,option,efts,
                                 cumulative,netAssets,dailyReturns])
            st.success("保存成功")
