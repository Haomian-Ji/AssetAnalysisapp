import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


import streamlit as st
from datetime import date, datetime, timedelta
import calendar

import yfinance as yf
import plotly.express as px
import os

from streamlit_calendar import calendar

# ========== 数据存储 ==========
DATA_FILE = "data/data_hmji.csv"



# 读取/保存数据函数
def load_data():
    return pd.read_csv(DATA_FILE, parse_dates=["date"])

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

st.subheader("资产总览")

dataframe= load_data()
if "totalAssets" in dataframe.columns:
    totalasseits = dataframe["totalAssets"].head(1).values[0]
    st.write("总资产",totalasseits)



# date,totalAssets,cash,stocks,option,efts,cumulative,netAssets,dailyReturns
col11, col12, col13, col14 = st.columns(4)
with col11:
    cash = dataframe["cash"].head(1).values[0]
    st.write("现金",cash)
with col12:
    stocks = dataframe["stocks"].head(1).values[0]
    st.write("股票",stocks)
with col13:
    option = dataframe["option"].head(1).values[0]
    st.write("期权",option)
with col14:
    efts = dataframe["efts"].head(1).values[0]
    st.write("EFTs",efts)



st.subheader("走势分析")


# 侧边栏设置
with st.sidebar:
    st.header("设置参数")
    start_date = st.date_input("起始日期", value=pd.to_datetime("2025-01-01"))
    end_date = st.date_input("结束日期", value=pd.to_datetime("today"))
    update_button = st.button("更新数据")

# 获取指数数据
@st.cache_data  # 缓存数据提高性能
def get_index_data(start, end):
    try:
        # 定义指数代码
        indexes = {
            "标普500": "^GSPC",
            "纳斯达克": "^IXIC"
        }
        
        # 获取数据
        data = yf.download(
            list(indexes.values()),
            start=start,
            end=end,
            group_by="ticker"
        )
        
        # 处理数据格式
        df = pd.DataFrame()
        for name, ticker in indexes.items():
            temp = data[ticker][['Close']].copy()
            temp.columns = [name]
            df = pd.concat([df, temp], axis=1)
        
        return df.dropna()
    
    except Exception as e:
        st.error(f"数据获取失败: {str(e)}")
        return pd.DataFrame()

# 主内容区
if update_button or not update_button:  # 初始自动加载
    with st.spinner("正在获取数据..."):
        df = get_index_data(start_date, end_date)

    if not df.empty:

        
        # 绘制交互式图表
        # st.subheader("历史走势")
        fig = px.line(df, 
                        x=df.index,
                        y=df.columns,
                        labels={"value": "", "variable": ""},
                        title="收益率走势")
        
        fig.update_layout(hovermode="x unified",
                            height=600,
                            legend=dict(orientation="h", yanchor="bottom", y=1.02))
        st.plotly_chart(fig, use_container_width=True)

            # 显示最新数据
        col1, col2 = st.columns(2)
        with col1:
            latest_dji = df.iloc[-1]["标普500"]
            st.metric("标普500", 
                        f"{latest_dji:,.2f}",
                        delta=f"{df['标普500'].pct_change()[-1]*100:.2f}%")
        
        with col2:
            latest_ixic = df.iloc[-1]["纳斯达克"]
            st.metric("纳斯达克", 
                        f"{latest_ixic:,.2f}",
                        delta=f"{df['纳斯达克'].pct_change()[-1]*100:.2f}%")
        
        
    else:
        st.warning("没有获取到有效数据，请检查日期范围或网络连接")

st.subheader("总资产走势")






st.subheader("收益日历")



# 配置日历参数
calendar_options = {
    "headerToolbar": {
        "left": "today prev,next",
        "center": "title",
        "right": "dayGridMonth"
    },
    "initialView": "dayGridMonth"  # 默认月视图
}


dates = dataframe["date"]
dailyReturns = dataframe["dailyReturns"]




calendar_events = []
# 显示日历

for index,date in enumerate(dates):
    
    st.write(date)
    dailyReturn = dailyReturns.head(index+1).values[0]
    st.write(dailyReturn)
    color = "#FF6B6B"
    if dailyReturn > 0:
        color = "#4ECDC4"

    calendar_events.append(

        {
            "title": str(dailyReturn),
            "start": date.strftime("%Y-%m-%d"),
            # "end": date.strftime("%Y-%m-%dT%H:%M:%S"),
            "allDay":True,
            "color": color
        }

    )

selected_date = calendar(events=calendar_events, options=calendar_options)



