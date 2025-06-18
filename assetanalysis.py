import matplotlib.font_manager
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
from datetime import date, datetime, timedelta
from streamlit_calendar import calendar
import plotly.express as px
import matplotlib.dates as mdates
import requeststockindex
import matplotlib
from matplotlib.ticker import FuncFormatter


# plt.rcParams['font.sans-serif'] = ['SimHei']  # Windows 系统常用
# plt.rcParams['font.sans-serif'] = ['PingFang SC']  # macOS 系统常用
# plt.rcParams['font.sans-serif'] = ['苹方-简']  # macOS 系统常用



plt.rcParams['axes.unicode_minus'] = False

# ========== 数据存储 ==========
username=st.session_state.get('username')
DATA_FILE = f"data/data_{username}.csv"

# 读取/保存数据函数
def load_data():
    return pd.read_csv(DATA_FILE, parse_dates=['date'])

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

# 定义百分比格式化函数
def to_percent(y, _):
    return f"{y*100:.1f}%"  # 格式化为1位小数+百分号




dataframe= load_data()
# dataframe['date'] = pd.to_datetime(dataframe['date']).dt.strftime("%Y-%m-%d")
# save_data(dataframe)

local_data = dataframe.set_index('date').sort_index()
if dataframe.empty:
    st.write("数据为空")
else:
    lastcol= local_data.iloc[-1]
    firstcol = local_data.iloc[0]
    tab1, tab2, tab3, tab4 = st.tabs(["资产总览", "走势分析","总资产走势","收益日历"])
    with tab1:
        st.subheader("资产总览")

        if "totalAssets" in dataframe.columns:
            totalAssets = lastcol["totalAssets"]
            st.write("总资产",totalAssets)

        #totalAssets,cash,stocks,option,efts,
        col11, col12, col13, col14 = st.columns(4)
        cash = lastcol["cash"]
        stocks = lastcol["stocks"]
        option = lastcol["option"]
        efts = lastcol["efts"]

        pct_cash = cash/ totalAssets
        pct_stocks = stocks/ totalAssets
        pct_option = option/ totalAssets
        pct_efts = efts/ totalAssets
        # 数据准备
        labels = ['cash', 'stocks', 'option', 'EFTs']
        sizes = [pct_cash, pct_stocks, pct_option,pct_efts]  # 各部分百分比（需确保总和为100）
        colors = ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99']


        plt.pie(
            sizes, 
            labels=labels, 
            colors=colors,
            autopct='%1.2f%%',  # 显示百分比格式
            wedgeprops={'width': 0.4, 'edgecolor': 'white'}  # 宽度控制环形大小
        # code utf-8
        )

        st.pyplot(plt)

        with col11:
            st.write("现金")
            st.markdown(
            f'<span style="color: #ff9999; font-weight: bold;">{cash}</span>',
            unsafe_allow_html=True
            )
        with col12:
            st.write("股票")
            st.markdown(
            f'<span style="color: #66b3ff; font-weight: bold;">{stocks}</span>',
            unsafe_allow_html=True
            )
        with col13:
            st.write("期权")
            st.markdown(
            f'<span style="color: #99ff99; font-weight: bold;">{option}</span>',
            unsafe_allow_html=True
            )
        with col14:
            st.write("EFTs")
            st.markdown(
            f'<span style="color: #ffcc99; font-weight: bold;">{efts}</span>',
            unsafe_allow_html=True
            )

    with tab2:
        st.subheader("收益率走势")
        # 选择周期
        period = st.selectbox("周期", ["年初至今","月初至今"],label_visibility="hidden")
        # st.write(period)

        # 确定开始日期，默认为年初开始
        yeardata=local_data.loc[local_data.index.year == datetime.today().year]
        firstnetassets = yeardata["totalAssets"].iloc[0]
        lastnetAssets = yeardata["totalAssets"].iloc[-1]
        start_date = datetime.today().strftime("%Y-01-01")
        end_date = datetime.today().strftime("%Y-%m-%d")
        # 去除出入资金列
        # assetsdata= yeardata["totalAssets"]
        assetsdata= yeardata.drop(columns=["money","change"])

        # 月初至今，数据重新计算
        if period == "月初至今":
            monthdata=yeardata.loc[yeardata.index.month == datetime.today().month]
            # st.write(monthdata)
            if monthdata.empty:
                firstnetassets = lastnetAssets
                st.caption("当月暂时没数据")
            else:
                firstnetassets = monthdata["totalAssets"].iloc[0]
            start_date = datetime.today().strftime("%Y-%m-01")
            assetsdata = monthdata.drop(columns=["money","change"])

        # st.write(assetsdata)
        # 显示收益及收益率
        cumulative =  lastnetAssets - firstnetassets
        cumulativerate = cumulative / firstnetassets

        col21, col22 =st.columns(2)
        with col21:
            st.metric("累计收益", 
                "累计收益",
                delta=f"{cumulative}",label_visibility="hidden")
        with col22:

            st.metric("收益率", 
                "收益率",
                delta=f"{cumulativerate*100:.2f}%",label_visibility="hidden")

        # 获取指数数据 
        nasdaq = requeststockindex.get_yd_index_data(start_date,end_date)
        # st.write(nasdaq)
        if nasdaq.empty :

            sp500_day=requeststockindex.get_polygon_daydata("I:SPX",start_date,end_date).set_index('date').sort_index()
            sp500_day = sp500_day.rename(columns={"close":"标普500"})

            # st.write(sp500_day)
            nasdaq_day=requeststockindex.get_polygon_daydata("I:COMP",start_date,end_date).set_index('date').sort_index()
            nasdaq_day = nasdaq_day.rename(columns={"close":"纳斯达克"})

            # st.write(nasdaq_day)
            nasdaq = pd.merge(
                sp500_day,
                nasdaq_day,
                left_index=True,
                right_index=True,
                how='inner'  # 只保留两者共有的日期
                
            )
        index_rate = nasdaq.apply(
            lambda x: ((x - x.iloc[0])/ x.iloc[0]) 
        )
        assets_rate = assetsdata.apply(
            lambda x: ((x - x.iloc[0])/ x.iloc[0]) 
        )
        # st.write(nasdaq)

        def draw_plot():
            # 第三部分：数据对齐与标准化
            # =============================================
            # 合并两个数据集（按日期对齐）
            combined = pd.merge(
                assets_rate,
                index_rate,
                left_index=True,
                right_index=True,
                # how='inner'  # 只保留两者共有的日期
                how = 'outer'
                
            )
            # st.write(combined)

            # 第四部分：绘制对比曲线
            # =============================================
            plt.figure(figsize=(12, 6))



            # 转换为 pandas Series 并插值填充缺失值
            s = pd.Series(combined['totalAssets'], index=combined.index)
            s_interp = s.interpolate(method='linear')  # 线性插值

            # 绘制资产曲线
            plt.plot(
                # combined.index,
                # combined['totalAssets'],
                s_interp.index, 
                s_interp.values,
                color='#3498db',
                linewidth=2,
                label='Asset'
            )

            # 绘制纳斯达克曲线
            plt.plot(
                combined.index,
                combined['纳斯达克'],
                color='#e74c3c',
                linewidth=2,
                linestyle='--',
                label='Nasdaq'
            )

            # 绘制标普500曲线
            plt.plot(
                combined.index,
                combined['标普500'],
                color='#ff99cc',
                linewidth=2,
                linestyle='--',
                label='S&P 500'
            )

            # 设置日期格式
            plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))

            plt.gcf().autofmt_xdate()
            plt.xticks([combined.index[0], combined.index[-1]])  # 只显示首尾日期

            # 应用格式化器到y轴
            formatter = FuncFormatter(to_percent)
            plt.gca().yaxis.set_major_formatter(formatter)

            # # 添加图表元素
            # plt.title("资产与纳斯达克指数走势对比（基准化）", fontsize=14, pad=20)
            # plt.xlabel("日期", fontsize=12)
            # plt.ylabel("标准化值（初始值=100）", fontsize=12)
            # plt.grid(True, linestyle='--', alpha=0.6)
            plt.legend(loc='upper left', frameon=False)

            # 显示图表
            plt.tight_layout()
            plt.show()

            st.pyplot(plt)

            col221, col222 = st.columns(2)
            with col221:
                latest_gspc = combined['标普500'].iloc[-1]
                st.metric("标普500", 
                            "标普500",
                            delta=f"{latest_gspc*100:.2f}%",label_visibility="hidden")

            with col222:
                latest_ixic = combined.iloc[-1]["纳斯达克"]
                st.metric("纳斯达克", 
                        "纳斯达克",
                            delta=f"{latest_ixic*100:.2f}%",label_visibility="hidden")


        if nasdaq.empty :
            st.write("数据获取失败")
        else:
            draw_plot()

    with tab3:
        st.subheader("总资产走势")

        col31, col32 = st.columns(2)
        dates = dataframe['date']
        netAssets = dataframe["totalAssets"]
        if netAssets.count() >1:
            dailyReturn= netAssets.iloc[-1] - netAssets.iloc[-2]
        else:
            dailyReturn = 0

        color = dailyReturn > 0 and "#4ECDC4" or "#FF6B6B"


        with col31:
            st.write("资产净值")
            st.write(netAssets.iloc[-1])
        with col32:
            st.write("当日收益")
            st.write(dailyReturn)


        # 创建画布
        plt.figure(figsize=(12, 6))

        # 绘制曲线
        plt.plot(
            dates, 
            dataframe["totalAssets"],
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
        st.divider()
        st.subheader("收益日历")

        selected = dataframe.loc[dataframe['money'].isnull()]


        dates = selected["date"]
        # st.write(local_data)
        # 去除出入资金的行列
        netAssets = local_data.loc[local_data['money'].isnull()]["totalAssets"]

        # st.write(netAssets)

        def get_monthreturn(selecteddate):

            yearnetAssets=netAssets.loc[netAssets.index.year == selecteddate.year]
            monthnetAssets=yearnetAssets.loc[yearnetAssets.index.month == selecteddate.month]
            if monthnetAssets.empty :
                return 0, 0
            
            monthfirst = monthnetAssets.iloc[0]
            month_return = monthnetAssets.iloc[-1] - monthfirst
            month_rate = month_return/ monthfirst * 100
            return month_return, month_rate

        month_return,month_rate =get_monthreturn(datetime.today())

        col41,col42 = st.columns(2)
        with col41:
            st.write(f"{datetime.today().month}月收益")
            st.write(month_return)
        with col42:
            st.write("收益率")
            st.write(f"{month_rate:+.2f}%")



        calendar_events = []

        for i,date in enumerate(dates):
            
            # st.write(date,i)
            dailyReturn = 0
            rate = 0
            if i > 0:
                dailyReturn=netAssets.iloc[i]-netAssets.iloc[i-1]
                rate= dailyReturn / netAssets.iloc[i-1]

            # result = x > 0 and "正数" or "非正数"
            color = dailyReturn > 0 and "#4ECDC4" or "#FF6B6B"

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
                    "title": str(f"{rate*100:.2f}%"),
                    "start": date.strftime("%Y-%m-%d"),
                    # "end": date.strftime("%Y-%m-%dT%H:%M:%S"),
                    "allDay":True,
                    "color": color
                }
            )
        # 显示日历



        # 配置日历参数
        calendar_options = {
            "headerToolbar": {
                "left": "today prev,next",
                "center": "title",
                "right": "dayGridMonth"
            },
            "initialView": "dayGridMonth",  # 默认月视图

            "contentHeight": "auto",
            # "navLinks": False,  # 禁用导航跳转
            "fixedWeekCount": False,  # 不固定周数
            "handleWindowResize": True,  # 启用窗口大小自适应
            "eventRenderWait": 100, # 延迟渲染
            # "loading": "function(bool) { if(bool) { /* 显示加载状态 */ } }"
            "height": "parent"

        }


        with st.container():
            st.markdown("""
            <style>
            .stCalendar {
                height: 600px;
                width: 100%;
            }
            </style>
            """, unsafe_allow_html=True)


        # 渲染日历
        try:
            result = calendar(
                events=calendar_events, 
                options=calendar_options,
                key="main_calendar"
            )
        except Exception as e:
            st.error(f"日历渲染失败: {str(e)}")








