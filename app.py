import streamlit as st

st.set_page_config(page_title='Bayaz Studio',page_icon=':material/auto_awesome:',layout='wide')
page=st.navigation([
    st.Page('builder_ui.py',title='Build websites',icon=':material/auto_awesome:',default=True),
    st.Page('chat_app.py',title='AI chat',icon=':material/chat:'),
])
page.run()
