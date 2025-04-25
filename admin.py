import streamlit as st
import streamlit_authenticator as stauth

import yaml
from yaml.loader import SafeLoader
from streamlit_authenticator.utilities import *

import csv
import datetime

# 打开用户文件
with open('data/config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

users = config['credentials']['usernames']
for key in users:
    username=key
    st.write(key)



# 自定义文件名（带日期示例）
# default_filename = f"data_{selected_date.strftime('%Y%m%d')}.csv"

default_filename = f"data_{username}.csv"
filename = st.text_input("保存文件名", value=default_filename)



with st.form("multi_field_form"):
    zongzichan = st.text_input("总资产")
    xianjin = st.text_input("现金")
    gupiao = st.text_input("股票")
    qiquan = st.text_input("期权")
    efts = st.text_input("EFTs")

    # 日期选择组件（默认今天）
    selected_date = st.date_input("选择日期", value=datetime.datetime.now())

    submitted = st.form_submit_button("提交")
    
    if submitted:
        if zongzichan and xianjin and gupiao and qiquan and efts :
            with open(filename, "a") as f:
                writer = csv.writer(f)
                writer.writerow([zongzichan, zongzichan])
            st.success("保存成功")
