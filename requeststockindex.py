import requests
from datetime import date, datetime, timedelta
import pandas as pd
import streamlit as st
import yfinance as yf



def get_index_data(symbol):
    url = f"https://api.polygon.io/v2/aggs/ticker/{symbol}/prev?adjusted=true&apiKey={API_KEY}"
    response = requests.get(url)
    return response.json()

# # 获取标普500数据
# sp500_data = get_index_data("I:SPX")
# print("S&P 500:", sp500_data)

# # 获取纳斯达克综合指数数据
# nasdaq_data = get_index_data("I:COMP")
# print("Nasdaq Composite:", nasdaq_data)


def get_polygon_data(symbol, start_timestamp, end_timestamp, timeframe="30/minute"):
    """从Polygon获取30分钟K线数据"""
    POLYGON_KEY = st.secrets["POLYGON_KEY"]

    if not POLYGON_KEY:
        print("错误: 未设置POLYGON_KEY环境变量")
        return None
        
    base_url = "https://api.polygon.io/v2/aggs/ticker"
    # 时间用毫秒时间戳 为了获取某些数据的延长时间段
    url = f"{base_url}/{symbol}/range/{timeframe}/{start_timestamp}/{end_timestamp}?adjusted=true&sort=asc&limit=50000&apiKey={POLYGON_KEY}&include_extended_hours=true"
    
    try:
        print(f"正在请求数据: {url}")
        response = requests.get(url)
        print(f"API响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if 'results' in data:
                results = data['results']
                print(f"获取到 {len(results)} 条K线数据")
                
                candles = []
                for result in results:
                    try:
                        candle = {
                            "time": datetime.fromtimestamp(result['t']/1000).strftime('%Y-%m-%dT%H:%M:%SZ'),
                            "open": result['o'],
                            "high": result['h'],
                            "low": result['l'],
                            "close": result['c'],
                            "volume": result.get('v', 0)  # 如果没有交易量数据，默认为0
                        }
                        candles.append(candle)
                    except KeyError as e:
                        print(f"处理K线数据时缺少字段: {str(e)}")
                        continue
                
                if not candles:
                    print("没有成功处理任何K线数据")
                    return None
                    
                return candles
            else:
                print("API响应中没有数据")
                return None
        else:
            print(f"API请求失败: {response.text}")
            return None
    except Exception as e:
        print(f"获取数据时发生错误: {str(e)}")
        return None



def get_polygon_daydata(symbol, start_timestamp, end_timestamp, timeframe="1/day"):
    """从Polygon获取日线K线数据"""
    POLYGON_KEY = st.secrets["POLYGON_KEY"]

    if not POLYGON_KEY:
        print("错误: 未设置POLYGON_KEY环境变量")
        return pd.DataFrame()
        
    base_url = "https://api.polygon.io/v2/aggs/ticker"
    # 时间用毫秒时间戳 为了获取某些数据的延长时间段
    url = f"{base_url}/{symbol}/range/{timeframe}/{start_timestamp}/{end_timestamp}?adjusted=true&sort=asc&limit=50000&apiKey={POLYGON_KEY}&include_extended_hours=true"
    
    try:
        # print(f"正在请求数据: {url}")
        response = requests.get(url)
        # print(f"API响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            # 转换为DataFrame
            df = pd.DataFrame(data["results"])  # 根据实际JSON结构调整
            df = df.rename(columns={"c":"close"})
            # df["month"] = pd.to_datetime(df["month"] + "-01")  # 添加日期 → "2023-01-01"

            # pd.to_datetime(df["date_str"], format="%d/%m/%Y")
            # pd.to_datetime(df["timestamp_column"], unit='ms').dt.strftime("%Y-%m-%d")
            df["date"]=pd.to_datetime(pd.to_datetime(df["t"], unit='ms').dt.strftime("%Y-%m-%d"))

            return df
        else:
            print(f"API请求失败: {response.text}")
            return pd.DataFrame()
    except Exception as e:
        print(f"获取数据时发生错误: {str(e)}")
        return pd.DataFrame()

# 获取指数数据
@st.cache_data  # 缓存数据提高性能
def get_yd_index_data(start, end):
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
