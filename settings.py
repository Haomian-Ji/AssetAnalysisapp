
import yaml
from yaml.loader import SafeLoader
import os

import streamlit as st
import streamlit_authenticator as stauth

st.write("修改密码")
password = st.text_input
hashpassword = stauth.Hasher.hash(password)
st.write(hashpassword)