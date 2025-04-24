import streamlit as st
import yaml
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth
from streamlit_authenticator.utilities import *

# 打开用户文件
with open('data/config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator =  stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']

)  
st.header("admin")

try:
    (email_of_registered_user,
     username_of_registered,
     name_of_registered_user) = authenticator.register_user(roles=["user","admin"])
    if email_of_registered_user:
        st.success("用户注册成功")
        with open ('data/config.yaml','w') as file:
            yaml.dump(config,file,default_flow_style=False, allow_unicode= True)
except RegisterError as e:
    st.error(e)