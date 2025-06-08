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

username = st.selectbox("选择一个用户", users)

default_filename = f"data/data_{username}.csv"
filename = st.text_input("保存文件名", value=default_filename)

# # 初始化数据文件
if not os.path.exists(filename):
    pd.DataFrame(columns=["date", "totalAssets","cash","stocks","option","efts","money","change"]).to_csv(filename, index=False)

tab1,tab2 = st.tabs(["资金分布","资金进出"])
with tab1:
    
    with st.form("multi_field_form"):
            # 日期选择组件（默认今天）
        selected_date = st.date_input("选择日期", value=datetime.datetime.now())
        cash = st.number_input("现金")
        stocks = st.number_input("股票")
        option = st.number_input("期权")
        efts = st.number_input("EFTs")

        submitted = st.form_submit_button("提交")
        
        if submitted:
            totalAssets = cash + stocks + option + efts


            with open(filename, "a") as f:
                writer = csv.writer(f)
                writer.writerow([selected_date,
                                totalAssets, cash,stocks,option,efts,
                                #  cumulative,
                                
                                #  dailyReturns
                                ])
            st.success("保存成功")


with tab2:

    df=pd.read_csv(default_filename, parse_dates=['date'])
    cash = 0
    totalAssets =0
    if df.empty == False:
        totalAssets=df["totalAssets"].iloc[-1]
        cash = df["cash"].iloc[-1]
        stocks = df["stocks"].iloc[-1]
        option = df["option"].iloc[-1]
        efts = df["efts"].iloc[-1]

    st.write(f"总资产:({totalAssets})")
    st.write(f"现金:({cash})")
    # 添加说明
    st.caption("说明：出金和分红不得大于现金值。")
    with st.form("money_form"):
        # 日期选择组件（默认今天）
        date = datetime.datetime.today()
        change=st.selectbox("变动类型",["入金","出金","分红"])
        money = st.number_input("资金")
        submitted = st.form_submit_button("提交")
    
        if submitted:
            if money > 0:
                valid = True
                newcash = 0
                # st.write(change)
                if change in ["出金","分红"]:
                    if money > cash  :
                        st.error("出金和分红不得大于现金值")
                        valid =False
                    else:
                        newcash = cash - money
                else:
                    newcash = cash + money
                                
                if valid:
                    newtotalAssets = newcash + stocks + option + efts

                    # 添加新行（索引自动递增）
                    # df.loc[len(df)] = [date.strftime("%Y-%m-%d"),newtotalAssets, newcash,stocks,option,efts,money,change]

                    # 覆盖已有行
                    # df.loc[df['date'] == date.strftime("%Y-%m-%d"), 
                    #        ["totalAssets","cash","stocks","option","efts","money","change"]] = [newtotalAssets, newcash,stocks,option,efts,money,change]
                    
                    # df.to_csv(default_filename, index=False)

                    with open(filename, "a") as f:
                        writer = csv.writer(f)
                        writer.writerow([date.strftime("%Y-%m-%d"),
                                        newtotalAssets, newcash,stocks,option,efts,money,change

                                        ])
                    st.success("操作成功")
                    st.write(f"变动后总资金为:({newtotalAssets}),现金为:({newcash})")
            else:
                st.error("请输入金额")
