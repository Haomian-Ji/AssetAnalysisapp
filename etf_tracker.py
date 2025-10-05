import streamlit as st
import yfinance as yf
import pandas as pd
import os
from datetime import datetime, timedelta
import time

# 设置页面
st.set_page_config(
    page_title="ETF收盘价追踪系统",
    page_icon="📊",
    layout="wide"
)

# 预定义的ETF列表
DEFAULT_ETFS = {
    "SPY": "SPDR S&P 500 ETF Trust",
    "QQQ": "Invesco QQQ Trust",
    "IWM": "iShares Russell 2000 ETF",
    "EEM": "iShares MSCI Emerging Markets ETF",
    "TLT": "iShares 20+ Year Treasury Bond ETF",
    "GLD": "SPDR Gold Shares",
    "VTI": "Vanguard Total Stock Market ETF",
    "VOO": "Vanguard S&P 500 ETF",
    "IVV": "iShares Core S&P 500 ETF",
    "DIA": "SPDR Dow Jones Industrial Average ETF"
}

class ETFDataManager:
    def __init__(self, data_file="etf_prices.csv"):
        self.data_file = data_file
        self.load_existing_data()
    
    def load_existing_data(self):
        """加载现有的CSV数据"""
        if os.path.exists(self.data_file):
            self.df = pd.read_csv(self.data_file, index_col=0, parse_dates=True)
            # 确保索引是日期格式
            self.df.index = pd.to_datetime(self.df.index)
        else:
            self.df = pd.DataFrame()
    
    def get_today_close_prices(self, etf_list):
        """获取今天的收盘价"""
        today = datetime.now().date()
        prices = {}
        
        for ticker in etf_list:
            try:
                etf = yf.Ticker(ticker)
                # 获取最近2天的数据以确保有今天的数据
                hist = etf.history(period="2d")
                
                if not hist.empty:
                    # 获取最新数据（应该是今天的数据）
                    latest_date = hist.index[-1].date()
                    close_price = hist['Close'].iloc[-1]
                    
                    # 检查是否是今天的数据（考虑闭市时间）
                    if latest_date == today:
                        prices[ticker] = close_price
                        st.success(f"✅ {ticker}: ${close_price:.2f} ({latest_date})")
                    else:
                        st.warning(f"⚠️ {ticker}: 今天尚无数据，最后更新 {latest_date}")
                else:
                    st.error(f"❌ {ticker}: 无法获取数据")
                    
            except Exception as e:
                st.error(f"❌ {ticker}: 错误 - {str(e)}")
                prices[ticker] = None
        
        return prices
    
    def update_data(self, etf_list):
        """更新数据到CSV文件"""
        today = datetime.now().date()
        
        # 检查今天是否已经更新过数据
        if not self.df.empty and today in self.df.index:
            st.info(f"📝 今天 ({today}) 的数据已经存在")
            return False
        
        st.info("🔄 正在获取今日收盘价...")
        today_prices = self.get_today_close_prices(etf_list)
        
        # 创建新的数据行
        new_row = {ticker: today_prices.get(ticker, None) for ticker in etf_list}
        new_row_df = pd.DataFrame([new_row], index=[pd.Timestamp(today)])
        
        # 合并到现有数据
        if self.df.empty:
            self.df = new_row_df
        else:
            self.df = pd.concat([self.df, new_row_df])
        
        # 保存到CSV
        self.df.to_csv(self.data_file)
        st.success(f"💾 数据已保存到 {self.data_file}")
        return True
    
    def get_data_summary(self):
        """获取数据概览"""
        if self.df.empty:
            return "暂无数据"
        
        return f"数据范围: {self.df.index[0].strftime('%Y-%m-%d')} 至 {self.df.index[-1].strftime('%Y-%m-%d')}，共 {len(self.df)} 个交易日"

def is_market_closed():
    """判断市场是否已收盘（美东时间）"""
    now_utc = datetime.utcnow()
    
    # 转换为美东时间（UTC-5，考虑夏令时简化处理）
    est_offset = -5 if now_utc.month in [11, 12, 1, 2] else -4
    now_est = now_utc + timedelta(hours=est_offset)
    
    # 美股交易时间：9:30 - 16:00 美东时间
    market_open = now_est.replace(hour=9, minute=30, second=0, microsecond=0)
    market_close = now_est.replace(hour=16, minute=0, second=0, microsecond=0)
    
    # 周末不交易
    if now_est.weekday() >= 5:  # 5=周六, 6=周日
        return True
    
    return now_est > market_close

def main():
    st.title("📊 ETF每日收盘价追踪系统")
    st.markdown("自动获取并保存ETF每日收盘价格到CSV文件")
    
    # 初始化数据管理器
    data_manager = ETFDataManager()
    
    # 侧边栏设置
    st.sidebar.header("🔧 设置")
    
    # ETF选择
    st.sidebar.subheader("选择ETF")
    selected_etfs = []
    for ticker, name in DEFAULT_ETFS.items():
        if st.sidebar.checkbox(f"{ticker} - {name}", value=True, key=ticker):
            selected_etfs.append(ticker)
    
    if not selected_etfs:
        st.warning("请至少选择一个ETF")
        return
    
    # 主内容区域
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📈 数据管理")
        
        # 手动更新按钮
        if st.button("🔄 手动更新今日数据", type="primary"):
            if is_market_closed():
                success = data_manager.update_data(selected_etfs)
                if success:
                    st.balloons()
            else:
                st.warning("⚠️ 市场尚未收盘，建议在闭市后更新数据")
        
        # 显示数据概览
        st.info(data_manager.get_data_summary())
        
        # 显示当前数据
        if not data_manager.df.empty:
            st.subheader("📋 历史数据")
            st.dataframe(data_manager.df.tail(10), use_container_width=True)
            
            # 下载数据按钮
            csv_data = data_manager.df.to_csv()
            st.download_button(
                label="📥 下载完整CSV数据",
                data=csv_data,
                file_name=f"etf_prices_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
    
    with col2:
        st.subheader("ℹ️ 系统信息")
        
        # 市场状态
        market_status = "已收盘" if is_market_closed() else "交易中"
        status_color = "green" if is_market_closed() else "orange"
        st.markdown(f"**市场状态:** <span style='color:{status_color}'>{market_status}</span>", unsafe_allow_html=True)
        
        st.markdown(f"**当前时间:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        st.markdown(f"**数据文件:** {data_manager.data_file}")
        st.markdown(f"**追踪ETF数量:** {len(selected_etfs)}")
        
        # 显示选中的ETF
        st.subheader("🎯 追踪的ETF")
        for etf in selected_etfs:
            st.write(f"- {etf}: {DEFAULT_ETFS[etf]}")
    
    # 数据可视化
    if not data_manager.df.empty and len(data_manager.df) > 1:
        st.subheader("📊 价格走势")
        
        # 计算涨跌幅
        price_changes = data_manager.df.pct_change().iloc[-1] * 100
        
        # 创建两个图表
        col_chart1, col_chart2 = st.columns(2)
        
        with col_chart1:
            # 最新价格柱状图
            latest_prices = data_manager.df.iloc[-1]
            fig1 = px.bar(
                x=latest_prices.index,
                y=latest_prices.values,
                title="最新收盘价",
                labels={'x': 'ETF', 'y': '价格 (USD)'}
            )
            st.plotly_chart(fig1, use_container_width=True)
        
        with col_chart2:
            # 近期涨跌幅
            if len(price_changes) > 0:
                fig2 = px.bar(
                    x=price_changes.index,
                    y=price_changes.values,
                    title="最新日涨跌幅 (%)",
                    color=price_changes.values,
                    color_continuous_scale="RdYlGn"
                )
                st.plotly_chart(fig2, use_container_width=True)

    # 自动更新功能（简化版）
    st.sidebar.subheader("自动更新")
    auto_update = st.sidebar.checkbox("启用自动更新", value=False)
    
    if auto_update:
        update_interval = st.sidebar.slider("检查间隔(分钟)", 5, 120, 30)
        
        if is_market_closed():
            st.sidebar.info(f"⏰ 自动更新已启用 - {update_interval}分钟后检查")
            
            # 简单的自动更新逻辑（实际部署时建议使用cron job）
            if st.sidebar.button("立即检查并更新"):
                data_manager.update_data(selected_etfs)
        else:
            st.sidebar.info("市场交易中，闭市后自动更新")

if __name__ == "__main__":
    main()