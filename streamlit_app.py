import streamlit as st
import streamlit_authenticator as stauth

import yaml
from yaml.loader import SafeLoader
from streamlit_authenticator.utilities import *


# 连接数据库
# conn = st.connection("snowflake")
# df = conn.query("SELECT * FROM mytable;", ttl="10m")

# for row in df.itertuples():
#     st.write(f"{row.NAME} has a :{row.PET}:")


if "role" not in st.session_state:
    st.session_state.role = None
    
ROLES = [None,"用户", "管理员"]

# 打开用户文件
with open('data/config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

# 定义登陆
def login():
    st.header("登录")
    role = st.selectbox("选择你的角色", ROLES)

    if role in ["用户", "管理员"]:
        # 从config.yaml加载用户数据
        authenticator =  stauth.Authenticate(
            config['credentials'],
            config['cookie']['name'],
            config['cookie']['key'],
            config['cookie']['expiry_days']
        )
        try:
            authenticator.login()
        except LoginError as e:
            st.error(e)

        if st.session_state.get('authentication_status'):
            st.write('欢迎 *%s*' % st.session_state.get('name'))
            st.session_state.role = role
            st.rerun()

        elif st.session_state.get('authentication_status') is False:
            st.error('用户名或密码错误')
        elif st.session_state.get('authentication_status') is None:
            st.warning('请输入你的用户名和密码')

def reset(dict1:dict):
    st.session_state.role = None

def logout():
    authenticator = stauth.authenticator(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days']
    )

    authenticator.logout(
        callback=reset
    )

role = st.session_state.role

logout_page = st.Page(logout, title="登出", icon=":material/logout:")
settings_page = st.Page("settings.py", title="设置", icon= ":material/settings:")
analysis_page = st.Page("assetanalysis.py")

admin_page = st.Page("admin.py", title="管理", icon=":material/logout:")

accout_pages = [logout_page, settings_page]
user_pages = [analysis_page]
admin_pages = [admin_page]

page_dict = {}
if st.session_state.role == "用户":
    page_dict["User"] = user_pages
elif st.session_state.role == "管理员":
    page_dict["Admin"] = admin_pages

if len(page_dict) > 0:
    pg = st.navigation({"Account": accout_pages} | page_dict)
else:
    pg = st.navigation([st.Page(login)])

pg.run()


        





