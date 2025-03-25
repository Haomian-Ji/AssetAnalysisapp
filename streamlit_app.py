import streamlit as st
import streamlit_authenticator as stauth

st.title("🎈 My new streamlit_authenticator app")
st.write(
    "Let's start building! For help and inspiration, head over to [docs.streamlit.io](https://docs.streamlit.io/)."
)

conn = st.connection("snowflake")
df = conn.query("SELECT * FROM mytable;", ttl="10m")

for row in df.itertuples():
    st.write(f"{row.NAME} has a :{row.PET}:")