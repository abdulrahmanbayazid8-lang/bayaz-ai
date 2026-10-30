import streamlit as st

st.set_page_config(page_title='Bayaz Studio',page_icon=':material/auto_awesome:',layout='wide')
page=st.navigation([
    st.Page('home_ui.py',title='Workspace',icon=':material/grid_view:',default=True),
    st.Page('builder_ui.py',title='Website builder',icon=':material/auto_awesome:'),
    st.Page('chat_app.py',title='AI tools',icon=':material/chat:'),
])
page.run()
