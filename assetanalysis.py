import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
from datetime import date, datetime, timedelta
from streamlit_calendar import calendar
import yfinance as yf
import plotly.express as px
import matplotlib.dates as mdates

plt.rcParams['font.sans-serif'] = ['SimHei']  # Windows 系统常用
plt.rcParams['font.sans-serif'] = ['PingFang SC']  # macOS 系统常用
plt.rcParams['axes.unicode_minus'] = False

# ========== 数据存储 ==========
username=st.session_state.get('username')
DATA_FILE = f"data/data_{username}.csv"



# 读取/保存数据函数
def load_data():
    return pd.read_csv(DATA_FILE, parse_dates=["date"])

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

dataframe= load_data()

tab1, tab2, tab3, tab4 = st.tabs(["资产总览", "走势分析","总资产走势","收益日历"])
with tab1:
    st.subheader("资产总览")

    
    if "totalAssets" in dataframe.columns:
        totalasseits = dataframe["totalAssets"].head(1).values[0]
        st.write("总资产",totalasseits)



    # date,totalAssets,cash,stocks,option,efts,cumulative,netAssets,dailyReturns
    col11, col12, col13, col14 = st.columns(4)
    length= dataframe.count()
    cash = dataframe["cash"].loc[length["cash"]-1]
    stocks = dataframe["stocks"].loc[length["stocks"]-1]
    option = dataframe["option"].loc[length["option"]-1]
    efts = dataframe["efts"].loc[length["efts"]-1]

    # 数据准备
    labels = ['cash', 'stocks', 'option', 'EFTs']
    sizes = [cash, stocks, option, efts]  # 各部分百分比（需确保总和为100）
    colors = ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99']


    plt.pie(
        sizes, 
        labels=labels, 
        colors=colors,
        autopct=None,
        wedgeprops={'width': 0.4, 'edgecolor': 'white'}  # 宽度控制环形大小
    # code utf-8
    )

    st.pyplot(plt)

    with col11:
        st.write("现金")
        st.markdown(
        f'<span style="color: #ff9999; font-weight: bold;">{cash}%</span>',
        unsafe_allow_html=True
        )
    with col12:
        st.write("股票")
        st.markdown(
        f'<span style="color: #66b3ff; font-weight: bold;">{stocks}%</span>',
        unsafe_allow_html=True
        )
    with col13:
        st.write("期权")
        st.markdown(
        f'<span style="color: #99ff99; font-weight: bold;">{option}%</span>',
        unsafe_allow_html=True
        )
    with col14:
        st.write("EFTs")
        st.markdown(
        f'<span style="color: #ffcc99; font-weight: bold;">{efts}%</span>',
        unsafe_allow_html=True
        )

with tab2:
    st.subheader("走势分析")

    col21, col22 =st.columns(2)
    with col21:
        st.write("累计收益")
    with col22:
        st.write("收益率")

    # 侧边栏设置
    with st.sidebar:
        st.header("设置时间")
        start_date = st.date_input("起始日期", value=pd.to_datetime("2025-01-01"))
        end_date = st.date_input("结束日期", value=pd.to_datetime("today"))
        update_button = st.button("更新数据")





    # 获取指数数据
    # @st.cache_data  # 缓存数据提高性能
    def get_index_data(start, end):
        # st.write(start)
        # st.write(end)

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
            # st.write(data)

            # 处理数据格式
            df = pd.DataFrame()
            for name, ticker in indexes.items():
                temp = data[ticker][['Close']].copy()
                temp.columns = [name]
                df = pd.concat([df, temp], axis=1)
            
            # st.write(df)
            return df.dropna()
        
        except Exception as e:
            st.error(f"数据获取失败: {str(e)}")
            return pd.DataFrame()


    # # 主内容区
    # if update_button or not update_button:  # 初始自动加载
    #     with st.spinner("正在获取数据..."):
    #         df = get_index_data(start_date, end_date)

    #     if not df.empty:


    #         # 绘制交互式图表
    #         # st.subheader("历史走势")
    #         fig = px.line(df, 
    #                         x=df.index,
    #                         y=df.columns,
    #                         labels={"value": "", "variable": ""},
    #                         title="收益率走势")
            
    #         fig.update_layout(hovermode="x unified",
    #                             height=600,
    #                             legend=dict(orientation="h", yanchor="bottom", y=1.02))
    #         st.plotly_chart(fig, use_container_width=True)

    #             # 显示最新数据
    #         col1, col2 = st.columns(2)
    #         with col1:
    #             latest_dji = df.iloc[-1]["标普500"]
    #             st.metric("标普500", 
    #                         f"{latest_dji:,.2f}",
    #                         delta=f"{df['标普500'].pct_change()[-1]*100:.2f}%")
            
    #         with col2:
    #             latest_ixic = df.iloc[-1]["纳斯达克"]
    #             st.metric("纳斯达克", 
    #                         f"{latest_ixic:,.2f}",
    #                         delta=f"{df['纳斯达克'].pct_change()[-1]*100:.2f}%")
            
            
    #     else:
    #         st.warning("没有获取到有效数据，请检查日期范围或网络连接")


    # 第一部分：读取本地 CSV 资产数据
    # =============================================
    # 读取 CSV 文件（假设列名为 timestamp 和 asset）
    # local_data = load_data().set_index('date').sort_index()
    local_data = pd.read_csv(
        DATA_FILE,  # 替换为你的文件路径
        parse_dates=['date'],
        usecols=['date', 'netAssets']
    ).set_index('date').sort_index()
    # st.write(local_data)
    # 第二部分：获取纳斯达克指数数据
    # =============================================
    # 定义时间范围（自动匹配本地数据的时间区间）
    start_date = local_data.index.min().strftime('%Y-%m-%d')
    end_date = local_data.index.max().strftime('%Y-%m-%d')

    nasdaq = get_index_data(start_date,end_date)

    # 第三部分：数据对齐与标准化
    # =============================================
    # 合并两个数据集（按日期对齐）
    combined = pd.merge(
        local_data,
        nasdaq,
        left_index=True,
        right_index=True,
        how='inner'  # 只保留两者共有的日期
        
    )
    # st.write(combined)
    # 标准化到相同起点（初始值设为 10000）
    combined_normalized = combined.apply(
        lambda x: ((x - x.iloc[0])/ x.iloc[0]) 
    )
    # st.write(combined_normalized)
    # 第四部分：绘制对比曲线
    # =============================================
    plt.figure(figsize=(12, 6))

    # 绘制资产曲线
    plt.plot(
        combined_normalized.index,
        combined_normalized['netAssets'],
        color='#3498db',
        linewidth=2,
        label='本地资产'
    )

    # 绘制纳斯达克曲线
    plt.plot(
        combined_normalized.index,
        combined_normalized['纳斯达克'],
        color='#e74c3c',
        linewidth=2,
        linestyle='--',
        label='纳斯达克指数'
    )

    # 绘制标普500曲线
    plt.plot(
        combined_normalized.index,
        combined_normalized['标普500'],
        color='#ff99cc',
        linewidth=2,
        linestyle='--',
        label='标普500'
    )

    # 设置日期格式
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    # plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=1))
    plt.gcf().autofmt_xdate()

    # # 添加图表元素
    # plt.title("资产与纳斯达克指数走势对比（基准化）", fontsize=14, pad=20)
    # plt.xlabel("日期", fontsize=12)
    # plt.ylabel("标准化值（初始值=100）", fontsize=12)
    # plt.grid(True, linestyle='--', alpha=0.6)
    # plt.legend(loc='upper left', frameon=False)

    # 显示图表
    plt.tight_layout()
    plt.show()

    st.pyplot(plt)


    col1, col2 = st.columns(2)
    len1=combined_normalized.count()
    with col1:
        latest_dji = combined_normalized.iloc[-1]['标普500']
        # st.write(latest_dji)
        st.metric("标普500", 
                    f"{latest_dji:,.2f}",
                    delta=f"{combined_normalized['标普500'].pct_change()[-1]*100:.2f}%")

    with col2:
        latest_ixic = combined_normalized.iloc[-1]["纳斯达克"]
        # st.write(latest_ixic)

        st.metric("纳斯达克", 
                    f"{latest_ixic:,.2f}",
                    delta=f"{combined_normalized['纳斯达克'].pct_change()[-1]*100:.2f}%")

with tab3:
    st.subheader("总资产走势")

    col31, col32 = st.columns(2)


    df = load_data()
    length= df.count()
    netAssets = df["netAssets"].loc[length["netAssets"]-1]

    with col31:
        st.write("资产净值")
        st.write(netAssets)
    with col32:
        st.write("当日收益")
        if length["netAssets"] > 1:
            dailyReturn= netAssets - df["netAssets"].loc[length["netAssets"]-2]
        else :
            dailyReturn =0
        color = "#4ECDC4"
        st.write(dailyReturn,color = color)

    # 检查数据格式
    # print("数据样例：\n", df.head())
    # print("\n数据类型：\n", df.dtypes)

    # 创建画布
    plt.figure(figsize=(12, 6))

    # 绘制曲线
    plt.plot(
        df['date'], 
        df['netAssets'],
        color='#2ecc71',   # 曲线颜色
        linewidth=2,       # 曲线粗细
        marker='o',        # 数据点标记
        markersize=4,      # 标记大小
        linestyle='-'      # 线型（实线）
    )

    # 设置时间轴格式
    plt.gca().xaxis.set_major_formatter(
        mdates.DateFormatter('%Y-%m-%d')  # 显示年月日
    )
    # plt.gca().xaxis.set_major_locator(
    #     mdates.AutoDateLocator()  # 自动选择刻度间隔
    # )
    plt.gcf().autofmt_xdate()  # 自动旋转日期标签

    # 添加标题和标签
    # plt.title("资产时间序列图", fontsize=14, fontweight='bold')
    # plt.xlabel("时间", fontsize=12)
    # plt.ylabel("资产（单位：万元）", fontsize=12)

    # 添加网格线
    # plt.grid(
    #     True, 
    #     linestyle='--', 
    #     alpha=0.5, 
    #     color='gray'
    # )

    # 显示图表
    plt.tight_layout()
    plt.show()

    st.pyplot(plt)

with tab4:
    st.subheader("收益日历")

    # 配置日历参数
    calendar_options = {
        "headerToolbar": {
            "left": "today prev,next",
            "center": "title",
            "right": "dayGridMonth"
        },
        "initialView": "dayGridMonth",  # 默认月视图

        "contentHeight": "auto",
        "navLinks": False,  # 禁用导航跳转
        "fixedWeekCount": False,  # 不固定周数
        "handleWindowResize": True,  # 启用窗口大小自适应
    }


    dates = dataframe["date"]
    # dailyReturns = dataframe["dailyReturns"]
    netAssets = dataframe["netAssets"]
    calendar_events = []
    # 显示日历

    for index,date in enumerate(dates):
        
        # st.write(date,index)
        dailyReturn=netAssets.iloc[index]-netAssets.iloc[0]
        # dailyReturn=dailyReturns.iloc[index]
        lv= dailyReturn / netAssets.iloc[0]
        # st.write(dailyReturn)
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
        
        calendar_events.append(

            {
                "title": str(f"{lv*100:.2f}%"),
                "start": date.strftime("%Y-%m-%d"),
                # "end": date.strftime("%Y-%m-%dT%H:%M:%S"),
                "allDay":True,
                "color": color
            }
        )
    selected_date = calendar(events=calendar_events, options=calendar_options,key="simple_calendar",)
    

