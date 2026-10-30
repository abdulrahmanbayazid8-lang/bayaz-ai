"""Emergent-inspired single-page website builder, powered by Groq."""
from collections import deque
from datetime import datetime, timezone
from io import BytesIO
import json
import threading
import time
import uuid
import zipfile

import streamlit as st
from builder_core import generate, generation_messages, preview_wrapper, friendly_error
from studio_ui import brand, privacy, artwork

st.set_page_config(page_title='Bayaz Studio — Build with AI',page_icon=':material/auto_awesome:',layout='wide')


class Allowance:
    def __init__(self):
        self.lock, self.day, self.count = threading.Lock(), None, 0

    def take(self,limit):
        with self.lock:
            today=datetime.now(timezone.utc).date()
            if self.day != today:
                self.day,self.count=today,0
            if self.count>=limit:
                raise ValueError('Today’s build allowance is used up. Please return tomorrow.')
            self.count+=1


@st.cache_resource
def allowance():
    return Allowance()


def project_zip(project,code):
    output=BytesIO()
    with zipfile.ZipFile(output,'w',zipfile.ZIP_DEFLATED) as archive:
        archive.writestr('index.html',code)
        archive.writestr('README.txt',
            'Built with Bayaz Studio\n\nOpen index.html in a browser.\n'
            'Review the code and test it before publishing. This is a static website.\n'
            'Any login, payment, database or email features require a real backend.\n'
            'Generated code is untrusted. Do not add private keys to browser code.\n')
    return output.getvalue()


def build(brief):
    now=time.monotonic()
    times=st.session_state.build_times
    while times and now-times[0]>=3600:
        times.popleft()
    if len(times)>=10:
        raise ValueError('This session has used its 10 builds this hour. Please try again later.')
    if times and now-times[-1]<15:
        raise ValueError('Please wait 15 seconds between builds.')
    project=st.session_state.projects.get(st.session_state.active_project)
    previous=project['versions'][-1]['html'] if project else ''
    messages=generation_messages(brief,previous)
    allowance().take(daily_limit)
    times.append(now)
    with st.status('Building your website…',expanded=True) as status:
        st.write('Turning your brief into a responsive page.')
        progress=st.empty()
        checkpoint=[0]
        def update(count):
            if count-checkpoint[0]>=700:
                progress.caption(f'Writing HTML, styles and interactions · {count:,} characters')
                checkpoint[0]=count
        code=generate(api_key,model,messages,progress=update)
        progress.caption('HTML received. Preparing your isolated preview.')
        if project is None:
            identity=uuid.uuid4().hex
            project={'id':identity,'name':brief.strip().split('\n')[0][:45], 'versions':[]}
            st.session_state.projects[identity]=project
            st.session_state.active_project=identity
        project['versions'].append({'brief':brief,'html':code})
        project['versions']=project['versions'][-5:]
        # Bound project and version storage in this browser session.
        while len(st.session_state.projects)>5:
            oldest=next(iter(st.session_state.projects))
            del st.session_state.projects[oldest]
        status.update(label='Your website is ready',state='complete',expanded=False)


st.session_state.setdefault('projects',{})
st.session_state.setdefault('active_project',None)
st.session_state.setdefault('build_times',deque())
st.session_state.setdefault('brief_seed','')
try:
    api_key=st.secrets.get('GROQ_API_KEY','')
    model=st.secrets.get('GROQ_MODEL','openai/gpt-oss-20b')
    daily_limit=max(1,int(st.secrets.get('DAILY_BUILD_LIMIT',40)))
except FileNotFoundError:
    api_key,model,daily_limit='','openai/gpt-oss-20b',40

with st.sidebar:
    brand()
    if st.button('New project',icon=':material/add:',width='stretch'):
        st.session_state.active_project=None
        st.session_state.brief_seed=''
        st.rerun()
    st.space('small')
    st.subheader('Your projects')
    if not st.session_state.projects:
        st.caption('Your next idea starts here.')
    for identity,project in reversed(list(st.session_state.projects.items())):
        if st.button(project['name'],key='project_'+identity,
                     icon=':material/web:',width='stretch',
                     type='primary' if identity==st.session_state.active_project else 'secondary'):
            st.session_state.active_project=identity
            st.rerun()
    st.space('large')
    st.badge('FREE WORKSPACE',color='violet',icon=':material/auto_awesome:')
    st.caption('Projects stay in this session. Download your code before leaving.')
    with st.expander('About your data'):
        st.write('Prompts and the current website code are sent to Groq. '
                 'Do not include secrets or private data. Preview code runs in an '
                 'isolated frame. Downloads contain the original generated code; '
                 'review it before opening or publishing.')
        st.write('This release builds single-page websites. Accounts, databases, '
                 'payments and automatic project hosting are not connected.')

if not api_key:
    st.info('The owner needs to connect the model in hosting secrets before building is available.')

active=st.session_state.projects.get(st.session_state.active_project)
if active is None:
    _,hero,_=st.columns([1,6,1])
    with hero:
        st.space('small')
        st.badge('THE WEBSITE BUILDER',icon=':material/auto_awesome:',color='violet')
        st.title('Start with an idea. :violet[Make it real.]')
        st.markdown('Your next website starts with a conversation. **Tell us what you imagine.**')
        st.caption('Build a landing page, portfolio or interactive browser tool with AI.')
        with st.form('create_project'):
            brief=st.text_area('Describe your website',key='brief_seed',height=160,
                placeholder='A beautiful portfolio for a photographer, with a gallery and warm earthy colors…',
                max_chars=3000)
            submitted=st.form_submit_button('Build my website',icon=':material/auto_awesome:',type='primary',disabled=not api_key,width='stretch')
        if submitted:
            if not brief.strip():
                st.warning('Describe the website you want to build first.')
            else:
                try:
                    build(brief.strip())
                    st.rerun()
                except Exception as exc:
                    st.error(friendly_error(exc))
        st.space('small')
        st.caption('NEED A STARTING POINT?')
        suggestions=[('Portfolio','A polished personal portfolio for a Python developer. Include skills, three projects, an about section and a contact link. Blue and white colors.'),
                     ('Business website','A stylish one-page website for a coffee shop called Daylight. Warm cream and brown colors, menu, story, location and opening hours.'),
                     ('Interactive tool','A useful study timer with start, pause and reset buttons, a task list and light/dark toggle. All data is temporary in browser memory.')]
        cols=st.columns(3)
        for col,(label,preset) in zip(cols,suggestions):
            with col:
                def choose(value=preset):
                    st.session_state.brief_seed=value
                with st.container(border=True):
                    st.image(artwork('Code helper' if label=='Interactive tool' else 'Writer' if label=='Portfolio' else 'AI chat'),width='stretch',alt=label+' starting point illustration')
                    st.button(label,on_click=choose,width='stretch',icon=':material/arrow_outward:')
        st.space('large')
        cols=st.columns(3)
        for col,(title,description) in zip(cols,[('Describe','Start with a simple idea.'),('Refine','Ask for changes in plain English.'),('Make it yours','Preview and download your website.')]):
            with col:
                st.subheader(title)
                st.caption(description)
else:
    st.subheader(active['name'])
    st.caption('YOUR WORKSPACE · SINGLE-PAGE WEBSITE')
    editor,preview=st.columns([2,5],gap='large')
    with editor:
        st.subheader('Build conversation')
        with st.container(height=350,border=True):
            for number,version in enumerate(active['versions'],1):
                with st.chat_message('user'):
                    st.write(version['brief'])
                with st.chat_message('assistant'):
                    st.write(f'Version {number} is ready to preview.')
        with st.form('revise_project'):
            change=st.text_area('What would you like to change?',height=130,max_chars=3000,
                               placeholder='Make the hero darker and add a pricing section…')
            revise=st.form_submit_button('Apply changes',type='primary',disabled=not api_key,width='stretch')
        if revise:
            if not change.strip():
                st.warning('Describe the changes first.')
            else:
                try:
                    build(change.strip())
                    st.rerun()
                except Exception as exc:
                    st.error(friendly_error(exc))
    with preview:
        controls=st.columns([3,2])
        with controls[0]:
            version_index=st.selectbox('Version',range(len(active['versions'])),
                index=len(active['versions'])-1,format_func=lambda i:f'Version {i+1}',
                key='version_'+active['id']+'_'+str(len(active['versions'])))
        with controls[1]:
            mode=st.segmented_control('View',['Preview','Code'],default='Preview',
                key='view_'+active['id'])
        code=active['versions'][version_index]['html']
        if mode=='Code':
            st.code(code,language='html')
        else:
            device=st.segmented_control('Preview size',['Desktop','Mobile'],default='Desktop')
            st.iframe(preview_wrapper(code,mobile=device=='Mobile'),height=750,
                      alt='Isolated preview of your generated website')
        with st.container(horizontal=True):
            st.download_button('Download website',data=code,file_name='index.html',mime='text/html',icon=':material/download:')
            st.download_button('Download project ZIP',data=project_zip(active,code),
                               file_name='bayaz-website.zip',mime='application/zip')
        st.caption('Preview network access is blocked. Email, payment and database features need a backend. '
                   'Your generated website is not automatically published; download it to host it separately.')
