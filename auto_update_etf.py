# auto_update_etf.py
import yfinance as yf
import pandas as pd
import os
from datetime import datetime, timedelta
import time

# 配置
ETF_LIST = ["SPY", "QQQ", "IWM", "EEM", "TLT", "GLD", "VTI", "VOO", "IVV", "DIA"]
DATA_FILE = "etf_prices.csv"

def is_market_closed():
    """判断市场是否已收盘"""
    now_utc = datetime.utcnow()
    est_offset = -5 if now_utc.month in [11, 12, 1, 2] else -4
    now_est = now_utc + timedelta(hours=est_offset)
    
    # 周末不交易
    if now_est.weekday() >= 5:
        return True
    
    # 交易时间：9:30 - 16:00 美东时间
    market_close = now_est.replace(hour=16, minute=0, second=0, microsecond=0)
    return now_est > market_close

def update_etf_prices():
    """更新ETF价格到CSV文件"""
    # 加载现有数据
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE, index_col=0, parse_dates=True)
        df.index = pd.to_datetime(df.index)
    else:
        df = pd.DataFrame()
    
    today = datetime.now().date()
    
    # 检查今天是否已经更新过
    if not df.empty and today in df.index:
        print(f"{today} 的数据已存在")
        return
    
    if not is_market_closed():
        print("市场尚未收盘，等待闭市后更新")
        return
    
    print("正在获取今日收盘价...")
    today_prices = {}
    
    for ticker in ETF_LIST:
        try:
            etf = yf.Ticker(ticker)
            hist = etf.history(period="2d")
            
            if not hist.empty:
                latest_date = hist.index[-1].date()
                close_price = hist['Close'].iloc[-1]
                
                if latest_date == today:
                    today_prices[ticker] = close_price
                    print(f"✅ {ticker}: ${close_price:.2f}")
                else:
                    print(f"⚠️ {ticker}: 今天尚无数据")
            else:
                print(f"❌ {ticker}: 无法获取数据")
                
        except Exception as e:
            print(f"❌ {ticker}: 错误 - {str(e)}")
            today_prices[ticker] = None
    
    # 更新数据
    new_row = pd.DataFrame([today_prices], index=[pd.Timestamp(today)])
    
    if df.empty:
        df = new_row
    else:
        df = pd.concat([df, new_row])
    
    df.to_csv(DATA_FILE)
    print(f"💾 数据已保存到 {DATA_FILE}")

if __name__ == "__main__":
    update_etf_prices()