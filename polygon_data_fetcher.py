import os
from datetime import datetime
import pandas as pd
from polygon import RESTClient
import streamlit as st
import argparse

def fetch_and_save_data(ticker, cash_amount, user, shares):
    """
    从Polygon获取股票数据并保存到CSV文件
    
    Args:
        api_key (str): Polygon API密钥
        ticker (str): 股票代码
        cash_amount (float): 现金金额
        user (str): 用户名
    """
    # 初始化Polygon客户端
    POLYGON_KEY = st.secrets["POLYGON_KEY"]
    client = RESTClient(POLYGON_KEY)
    
    # 获取当前日期
    today = datetime.now().strftime('%Y-%m-%d')
    
    # 获取股票数据
    try:
        # 获取股票当前价格
        ticker_details = client.get_ticker_details(ticker)
        current_price = ticker_details.last_price
        
        # 准备数据行
        data_row = f"{today},{cash_amount + current_price*shares},{cash_amount},0.0,0.0,{current_price*shares}"
        
        # 确保数据目录存在
        data_dir = "/home/jokerjhm/AssetAnalysisapp/data"
        os.makedirs(data_dir, exist_ok=True)
        
        # 文件路径
        file_path = os.path.join(data_dir, f"data_{user}.csv")
        
        # 写入数据
        with open(file_path, 'a') as f:
            f.write(data_row + '\n')
            
        print(f"数据已成功保存到 {file_path}")
        
    except Exception as e:
        print(f"获取数据时发生错误: {str(e)}")

def main():
    parser = argparse.ArgumentParser(description='从Polygon获取股票数据并保存到CSV')
    parser.add_argument('--ticker', required=True, help='股票代码')
    parser.add_argument('--cash', type=float, required=True, help='现金金额')
    parser.add_argument('--user', required=True, help='用户名')
    parser.add_argument('--shares', type=float, required=True, help='股票数量')
    args = parser.parse_args()
    
    fetch_and_save_data(args.ticker, args.cash, args.user, args.shares)

if __name__ == "__main__":
    main() 