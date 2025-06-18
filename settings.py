
import yaml
from yaml.loader import SafeLoader
import os

import streamlit as st
import streamlit_authenticator as stauth
from streamlit_authenticator.utilities import *

st.write("修改密码")
# password = st.text_input
# hashpassword = stauth.Hasher.hash(password)
# st.write(hashpassword)

authenticator =  st.session_state.authenticator


config = st.session_state.config


# Creating a password reset widget
if st.session_state.get('authentication_status'):
    try:
        if authenticator.reset_password(st.session_state['username']):
            st.success('Password modified successfully')
    except (CredentialsError, ResetError) as e:
        st.error(e)



# Saving config file
with open('data/config.yaml', 'w', encoding='utf-8') as file:
    yaml.dump(config, file, default_flow_style=False, allow_unicode=True)