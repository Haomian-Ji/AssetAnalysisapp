# auto_update_etf.py
import yfinance as yf
import pandas as pd
import os
from datetime import datetime, timedelta
import sys

# 配置
ETF_LIST = ["SPY", "QQQ", "IWM", "EEM", "TLT", "GLD", "VTI", "VOO", "IVV", "DIA"]
DATA_FILE = "etf_prices.csv"

def is_trading_day():
    """判断是否为交易日"""
    today = datetime.now().date()
    # 周末不是交易日
    if today.weekday() >= 5:
        return False
    
    # 这里可以添加美国市场假日判断
    # 简化版本：暂时只排除周末
    return True

def is_market_closed():
    """判断市场是否已收盘（美东时间）"""
    if not is_trading_day():
        return False
        
    now_utc = datetime.utcnow()
    # 美东时间偏移（简化处理）
    est_offset = -4 if datetime.now().month in [3, 4, 5, 6, 7, 8, 9, 10] else -5
    now_est = now_utc + timedelta(hours=est_offset)
    
    # 美股交易时间：9:30 - 16:00 美东时间
    market_close = now_est.replace(hour=16, minute=0, second=0, microsecond=0)
    
    return now_est > market_close

def update_etf_prices():
    """更新ETF价格到CSV文件"""
    print(f"开始更新ETF价格 - {datetime.now()}")
    
    # 检查是否交易日且市场已收盘
    if not is_trading_day():
        print("今天不是交易日")
        return False
        
    if not is_market_closed():
        print("市场尚未收盘")
        return False
    
    # 加载现有数据
    if os.path.exists(DATA_FILE):
        try:
            df = pd.read_csv(DATA_FILE, index_col=0, parse_dates=True)
            df.index = pd.to_datetime(df.index)
            print(f"加载现有数据，共 {len(df)} 条记录")
        except Exception as e:
            print(f"加载现有数据失败，创建新文件: {e}")
            df = pd.DataFrame()
    else:
        df = pd.DataFrame()
        print("创建新的数据文件")
    
    today = datetime.now().date()
    
    # 检查今天是否已经更新过
    if not df.empty and today in [idx.date() for idx in df.index]:
        print(f"{today} 的数据已存在")
        return True
    
    print("正在获取今日收盘价...")
    today_prices = {}
    success_count = 0
    
    for ticker in ETF_LIST:
        try:
            etf = yf.Ticker(ticker)
            # 获取最近5天数据
            hist = etf.history(period="5d")
            
            if not hist.empty:
                latest_date = hist.index[-1].date()
                close_price = hist['Close'].iloc[-1]
                
                if latest_date == today:
                    today_prices[ticker] = close_price
                    success_count += 1
                    print(f"✅ {ticker}: ${close_price:.2f}")
                else:
                    today_prices[ticker] = None
                    print(f"⚠️ {ticker}: 今天尚无数据，最后更新 {latest_date}")
            else:
                today_prices[ticker] = None
                print(f"❌ {ticker}: 无法获取数据")
                
        except Exception as e:
            today_prices[ticker] = None
            print(f"❌ {ticker}: 错误 - {str(e)}")
    
    # 只有成功获取到数据时才更新
    if success_count > 0:
        # 更新数据
        new_row = pd.DataFrame([today_prices], index=[pd.Timestamp(today)])
        
        if df.empty:
            df = new_row
        else:
            df = pd.concat([df, new_row])
        
        # 按日期排序
        df = df.sort_index()
        
        df.to_csv(DATA_FILE)
        print(f"💾 数据已保存到 {DATA_FILE}，成功更新 {success_count}/{len(ETF_LIST)} 个ETF")
        return True
    else:
        print("❌ 没有成功获取到任何ETF数据")
        return False

if __name__ == "__main__":
    success = update_etf_prices()
    sys.exit(0 if success else 1)