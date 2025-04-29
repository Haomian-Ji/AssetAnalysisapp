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

# # 初始化数据文件
if not os.path.exists(DATA_FILE):
    pd.DataFrame(columns=["date", "note"]).to_csv(DATA_FILE, index=False)

# 读取/保存数据函数
def load_data():
    return pd.read_csv(DATA_FILE, parse_dates=["date"])

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

# # ========== 日历生成 ==========
# def generate_calendar(year, month, notes_df):
#     cal = calendar.monthcalendar(year, month)
#     month_days = []
    
#     for week in cal:
#         week_days = []
#         for day in week:
#             if day == 0:
#                 week_days.append("")
#                 continue
                
#             current_date = date(year, month, day)
#             # 检查是否有备注
#             notes = notes_df[notes_df["date"] == str(current_date)]["note"].tolist()
#             note_display = "📌 " + "<br>".join(notes) if notes else ""
            
#             week_days.append(f"""
#                 <div style='border:1px solid #eee; padding:10px; height:100px;
#                     {'background:#ffd70033;' if current_date == date.today() else ''}'>
#                     <b>{day}</b>
#                     <div style='font-size:0.8em; color:#666; overflow:hidden'>{note_display}</div>
#                 </div>
#             """)
#         month_days.append(week_days)
    
#     return pd.DataFrame(
#         month_days,
#         columns=["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
#     )

# # ========== 主界面 ==========
# st.title("📅 日历备注系统")

# # 选择年月
# col1, col2 = st.columns(2)
# with col1:
#     selected_year = st.selectbox("选择年份", range(2020, 2031), index=date.today().year-2020)
# with col2:
#     selected_month = st.selectbox("选择月份", range(1,13), index=date.today().month-1)

# # 生成日历
# notes_df = load_data()
# calendar_html = generate_calendar(selected_year, selected_month, notes_df).to_html(escape=False, index=False)
# st.markdown(f"<div style='font-family: Arial'>{calendar_html}</div>", unsafe_allow_html=True)

# # ========== 备注管理 ==========
# st.markdown("---")
# selected_date = st.date_input("选择日期添加/查看备注")

# # 获取选中日期的备注
# existing_notes = notes_df[notes_df["date"] == str(selected_date)]["note"].tolist()

# # 添加新备注
# new_note = st.text_input("输入新备注", key=f"note_{selected_date}")
# if st.button("💾 保存备注") and new_note:
#     updated_df = pd.concat([
#         notes_df,
#         pd.DataFrame([[selected_date, new_note]], columns=["date", "note"])
#     ])
#     save_data(updated_df)
#     st.experimental_rerun()

# # 显示已有备注
# if existing_notes:
#     st.subheader("已有备注")
#     for note in existing_notes:
#         st.markdown(f"- {note}")
# else:
#     st.info("该日期暂无备注")

# # ========== 样式优化 ==========
# st.markdown("""
# <style>
#     table {width:100% !important;}
#     td {vertical-align: top !important;}
#     div[data-testid="stMarkdown"] {line-height: 1.5;}
# </style>
# """, unsafe_allow_html=True)


# 配置日历参数
calendar_options = {
    "headerToolbar": {
        "left": "today prev,next",
        "center": "title",
        "right": "dayGridMonth"
    },
    "initialView": "dayGridMonth"  # 默认月视图
}

# 显示日历
calendar_events = [
    {
        "title": "会议",
        "start": "2025-04-15T10:00:00",
        "end": "2025-04-15T12:00:00",
        "color": "#FF6B6B"
    },
    {
        "title": "项目里程碑",
        "start": "2025-04-20",
        "allDay": True,
        "color": "#4ECDC4"
    }
]

selected_date = calendar(events=calendar_events, options=calendar_options)
# st.write("当前选中日期范围:", selected_date)

# 设置页面标题
st.set_page_config(page_title="美股指数实时监控", layout="wide")

# 安装提示（如果缺少库）
# pip install streamlit yfinance pandas plotly

# 页面标题
st.title("📈 道琼斯 & 纳斯达克指数监控")

# 侧边栏设置
with st.sidebar:
    st.header("设置参数")
    start_date = st.date_input("起始日期", value=pd.to_datetime("2023-01-01"))
    end_date = st.date_input("结束日期", value=pd.to_datetime("today"))
    update_button = st.button("更新数据")

# 获取指数数据
@st.cache_data  # 缓存数据提高性能
def get_index_data(start, end):
    try:
        # 定义指数代码
        indexes = {
            "道琼斯工业平均指数": "^DJI",
            "纳斯达克综合指数": "^IXIC"
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
        # 显示最新数据
        col1, col2 = st.columns(2)
        with col1:
            latest_dji = df.iloc[-1]["道琼斯工业平均指数"]
            st.metric("道琼斯最新指数", 
                     f"{latest_dji:,.2f}",
                     delta=f"{df['道琼斯工业平均指数'].pct_change()[-1]*100:.2f}%")
        
        with col2:
            latest_ixic = df.iloc[-1]["纳斯达克综合指数"]
            st.metric("纳斯达克最新指数", 
                     f"{latest_ixic:,.2f}",
                     delta=f"{df['纳斯达克综合指数'].pct_change()[-1]*100:.2f}%")
        
        # 绘制交互式图表
        st.subheader("历史走势")
        fig = px.line(df, 
                     x=df.index,
                     y=df.columns,
                     labels={"value": "指数值", "variable": "指数名称"},
                     title="双指数对比走势图")
        
        fig.update_layout(hovermode="x unified",
                         height=600,
                         legend=dict(orientation="h", yanchor="bottom", y=1.02))
        st.plotly_chart(fig, use_container_width=True)
        
        # # 显示原始数据
        # st.subheader("历史数据")
        # col3, col4 = st.columns(2)
        # with col3:
        #     st.dataframe(df.style.format("{:,.2f}"), height=300)
        # with col4:
        #     st.download_button(
        #         label="下载CSV数据",
        #         data=df.to_csv().encode('utf-8'),
        #         file_name='stock_index_data.csv',
        #         mime='text/csv'
        #     )
        
        # # 相关性分析
        # st.subheader("指数相关性分析")
        # corr = df.corr().iloc[0,1]
        # st.write(f"相关系数：{corr:.2f}")
        # st.progress((corr + 1)/2)  # 将相关系数转换为0-1范围
        
    else:
        st.warning("没有获取到有效数据，请检查日期范围或网络连接")