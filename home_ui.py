import streamlit as st
from studio_ui import TOOLS, artwork, brand, privacy

st.set_page_config(page_title='Bayaz Studio — Your AI workspace',page_icon=':material/auto_awesome:',layout='wide')

with st.sidebar:
    brand()
    st.space('small')
    st.badge('FREE WORKSPACE',color='violet',icon=':material/auto_awesome:')
    st.space('medium')
    st.caption('QUICK ACCESS')
    for name in ['Writer','Summarizer','Code helper']:
        if st.button(name,icon=f":material/{TOOLS[name]['icon']}:",width='stretch'):
            st.session_state.selected_tool=name
            st.switch_page('chat_app.py')
    st.space('medium')
    privacy()

top=st.container(horizontal=True)
with top:
    st.badge('BAYAZ STUDIO',color='violet')
    st.caption('WRITE · LEARN · CREATE · BUILD')
st.space('small')
st.title('Less busywork. :violet[More possibility.]')
st.markdown('Your ideas deserve a head start. **Find the right AI tool and make something great.**')
st.caption('One workspace for writing, documents, code, interview practice and websites.')

with st.container(border=True):
    with st.form('workspace_start'):
        idea=st.text_area('What would you like to work on?',height=100,max_chars=3000,
                         placeholder='Write a professional email, explain some code, or build a website…')
        a,b=st.columns([3,2],vertical_alignment='bottom')
        with a:
            destination=st.selectbox('Choose your tool',list(TOOLS)+['Website builder'],label_visibility='collapsed')
        with b:
            start=st.form_submit_button('Let’s create',type='primary',icon=':material/arrow_forward:',width='stretch')
        if start:
            if destination=='Website builder':
                st.session_state.active_project=None
                st.session_state.brief_seed=idea.strip()
                st.switch_page('builder_ui.py')
            else:
                st.session_state.selected_tool=destination
                if idea.strip():
                    st.session_state.pending_prompt=idea.strip()
                st.switch_page('chat_app.py')

st.space('medium')
st.subheader('A little help. A lot of possibilities.')
st.caption('Six focused assistants, ready when you are.')
items=list(TOOLS.items())
for offset in [0,3]:
    columns=st.columns(3,gap='medium')
    for col,(name,info) in zip(columns,items[offset:offset+3]):
        with col:
            with st.container(border=True):
                st.image(artwork(name),width='stretch',alt=f'{name} assistant illustration')
                st.caption(info['tag'])
                st.subheader(name)
                st.write(info['subtitle'])
                if st.button('Open '+name.lower(),key='open_'+name,
                             icon=f":material/{info['icon']}:",width='stretch'):
                    st.session_state.selected_tool=name
                    st.switch_page('chat_app.py')

st.space('medium')
with st.container(border=True):
    left,right=st.columns([3,1],vertical_alignment='center')
    with left:
        st.badge('BUILD SOMETHING NEW',color='violet')
        st.subheader('An idea today. A website in minutes.')
        st.write('Describe it, refine it, preview it. Download a website that’s yours to keep.')
    with right:
        if st.button('Open website builder',type='primary',icon=':material/web:',width='stretch'):
            st.switch_page('builder_ui.py')
st.caption('Powered by Groq · Free usage limits apply · Review AI outputs before using them')
