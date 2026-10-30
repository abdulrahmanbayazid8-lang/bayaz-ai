import hashlib
from collections import deque
import time

import streamlit as st
from studio_ui import TOOLS, brand, privacy
from tool_prompts import STARTERS, prepare_messages
from cloud_backend import cloud_stream, failure_message, read_pdf, retrieve, usage_limit

st.set_page_config(page_title='Bayaz Studio — AI tools',page_icon=':material/auto_awesome:',layout='wide')
st.session_state.setdefault('selected_tool','AI chat')
st.session_state.setdefault('tool_threads',{})
st.session_state.setdefault('tool_times',deque())
try:
    api_key=st.secrets.get('GROQ_API_KEY','')
    model=st.secrets.get('GROQ_MODEL','openai/gpt-oss-20b')
    limit=max(1,int(st.secrets.get('DAILY_REQUEST_LIMIT',100)))
except FileNotFoundError:
    api_key,model,limit='','openai/gpt-oss-20b',100

with st.sidebar:
    brand()
    st.space('small')
    tool=st.selectbox('Your assistant',list(TOOLS),key='selected_tool')
    tone=st.selectbox('Response tone',['Professional','Friendly','Concise','Detailed'])
    target=st.selectbox('Target language',['English','Hindi','Spanish','French','Arabic','German','Portuguese','Tamil','Telugu','Bengali']) if tool=='Translator' else 'English'
    st.space('small')
    upload=st.file_uploader('Add a source document',type=['pdf','txt'],help='PDF or UTF-8 text, up to 5 MB. Source text is sent to Groq with your request.')
    st.caption('Optional · PDF / TXT · up to 5 MB')
    st.space('medium')
    privacy()

chunks=[]
document_id=None
if upload:
    data=upload.getvalue()
    document_id=hashlib.sha256(data).hexdigest()
    try:
        if len(data)>5*1024*1024:
            raise ValueError('Please use a document smaller than 5 MB.')
        if st.session_state.get('tools_document_id')!=document_id:
            if upload.name.lower().endswith('.pdf'):
                parsed=read_pdf(data)
            else:
                text=data.decode('utf-8-sig').strip()
                if not text:
                    raise ValueError('The text file is empty.')
                words=text.split()
                parsed=[{'page':1,'text':' '.join(words[i:i+200])} for i in range(0,len(words),160)]
            st.session_state.tools_document_chunks=parsed
            st.session_state.tools_document_id=document_id
        chunks=st.session_state.tools_document_chunks
    except Exception:
        st.error('Could not read this document. Use a text-based PDF of up to 50 pages or a UTF-8 TXT file under 5 MB.')
        st.stop()

thread_key=tool+':'+str(document_id)
threads=st.session_state.tool_threads
threads.setdefault(thread_key,[])
while len(threads)>8:
    key=next(k for k in threads if k!=thread_key)
    del threads[key]
history=threads[thread_key]
with st.sidebar:
    if st.button('New conversation',icon=':material/add:',width='stretch'):
        threads[thread_key]=[]
        st.session_state.pop('pending_prompt',None)
        st.rerun()
    if history:
        transcript='\n\n'.join(f"{m['role'].upper()}: {m['content']}" for m in history)
        st.download_button('Export conversation',transcript,'bayaz-conversation.txt','text/plain',width='stretch')
    st.caption('Each assistant has its own conversation. Recent context is limited to 3 exchanges; export anything you want to keep.')

info=TOOLS[tool]
st.badge(info['tag'],color='violet',icon=f":material/{info['icon']}:")
st.title(tool)
st.markdown(info['subtitle'])
if upload:
    st.caption('Source attached: '+upload.name)
if not api_key:
    st.info('The owner needs to connect the online model in the hosting secrets.')

chosen=None
if not history:
    st.space('small')
    with st.container(border=True):
        st.subheader('A good place to start')
        for label,example in STARTERS[tool]:
            if st.button(label,key='starter_'+tool+'_'+label,icon=':material/arrow_outward:',disabled=not api_key):
                chosen=example
    st.caption('Or type your own request below. These are AI assistants, not web search or code execution tools.')

for message in history:
    with st.chat_message(message['role']):
        st.markdown(message['content'])
        if message.get('sources'):
            with st.expander('Source passages'):
                for item in message['sources']:
                    st.markdown(f"**Page {item['page']}**")
                    st.write(item['text'])

typed=st.chat_input('Ask your '+tool.lower()+'…',max_chars=3000,submit_mode='disable',disabled=not api_key)
pending=st.session_state.pop('pending_prompt',None)
prompt=typed or chosen or pending
if prompt and prompt.strip() and api_key:
    prompt=prompt.strip()
    times=st.session_state.tool_times
    now=time.monotonic()
    while times and now-times[0]>=3600:
        times.popleft()
    try:
        if times and now-times[-1]<10:
            raise ValueError('Please wait 10 seconds between requests.')
        if len(times)>=20:
            raise ValueError('You’ve used this session’s 20 requests for the hour. Please return later.')
        usage_limit().reserve(limit)
    except ValueError as exc:
        st.warning(str(exc))
        st.stop()
    times.append(now)
    sources,context=[],''
    if chunks:
        if tool in ['Summarizer','Translator']:
            # Preserve page labels and explain the bounded excerpt to users.
            pieces=[]
            count=0
            for item in chunks:
                piece=f"[Page {item['page']}]\n{item['text']}"
                if count+len(piece)>8500:
                    break
                pieces.append(piece)
                sources.append(item)
                count+=len(piece)
            context='\n\n'.join(pieces)
            if len(sources)<len(chunks):
                st.info('This request uses the opening excerpt of your document, not the full file. For complete coverage, split long documents into smaller files.')
        else:
            sources=retrieve(prompt,chunks)
            context='\n\n'.join(f"[Page {c['page']}]\n{c['text']}" for c in sources) or 'No matching document passages were found.'
    messages=prepare_messages(tool,history,prompt,tone,target,context)
    parts,failed=[],False
    with st.chat_message('user'):
        st.write(prompt)
    with st.chat_message('assistant'):
        try:
            def tokens():
                for token in cloud_stream(api_key,model,messages):
                    parts.append(token)
                    yield token
            with st.spinner('Working on your request…'):
                st.write_stream(tokens())
            if not parts:
                raise RuntimeError('Empty response')
        except Exception as exc:
            failed=True
            parts.append('\n\n'+failure_message(exc))
    if chunks and tool in ['Summarizer','Translator'] and len(sources)<len(chunks):
        parts.append('\n\n*Based on the opening document excerpt only.*')
    history.extend([{'role':'user','content':prompt,'failed':failed},
                    {'role':'assistant','content':''.join(parts),'failed':failed,'sources':sources}])
    threads[thread_key]=history[-40:]
    st.rerun()
