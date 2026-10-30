"""Original vector artwork and shared native Streamlit branding."""
import streamlit as st

TOOLS = {
    'AI chat': {'icon':'chat','tag':'THINK IT THROUGH','subtitle':'A thinking partner for everyday questions.', 'color':'#9A86FF'},
    'Writer': {'icon':'edit_note','tag':'FIND YOUR WORDS','subtitle':'Emails, posts and polished first drafts.', 'color':'#6BCAFF'},
    'Summarizer': {'icon':'subject','tag':'GET THE ESSENTIALS','subtitle':'Turn long documents into clear takeaways.', 'color':'#7CE8C4'},
    'Translator': {'icon':'translate','tag':'GO BEYOND BORDERS','subtitle':'Translate naturally, with the right tone.', 'color':'#F6C578'},
    'Code helper': {'icon':'code','tag':'BUILD WITH CLARITY','subtitle':'Explain code, debug and explore solutions.', 'color':'#B8A1FF'},
    'Interview coach': {'icon':'forum','tag':'PRACTISE YOUR NEXT STEP','subtitle':'Prepare answers and work through questions.', 'color':'#F5A3C8'},
}


def artwork(kind='AI chat'):
    color = TOOLS.get(kind,{}).get('color','#9A86FF')
    # Decorative illustration, not a screenshot or a claim about real output.
    designs={
        'AI chat':'<rect x="56" y="42" width="215" height="38" rx="13" fill="ACCENT" opacity=".22"/><rect x="111" y="94" width="204" height="42" rx="13" fill="#ffffff" opacity=".09"/><path d="M74 60h130m-75 54h118" stroke="#eeeaff" stroke-width="5" stroke-linecap="round"/>',
        'Writer':'<rect x="85" y="24" width="194" height="136" rx="14" fill="#ffffff" opacity=".06"/><path d="M111 54h83m-83 23h140m-140 19h123m-123 19h95" stroke="ACCENT" stroke-width="5" stroke-linecap="round"/><path d="M242 133l35-35 13 13-35 35-18 5z" fill="ACCENT"/>',
        'Summarizer':'<path d="M57 45h100m-100 18h86m-86 18h100m-100 18h70m-70 18h100m-100 18h88" stroke="#b7c0d7" stroke-width="4" stroke-linecap="round"/><path d="M177 89h31m-8-8 8 8-8 8" stroke="ACCENT" stroke-width="3" fill="none"/><rect x="230" y="43" width="81" height="96" rx="12" fill="ACCENT" opacity=".15"/><path d="M246 65h45m-45 22h32m-32 22h38" stroke="ACCENT" stroke-width="4" stroke-linecap="round"/>',
        'Translator':'<circle cx="182" cy="91" r="66" fill="none" stroke="ACCENT" stroke-width="2" opacity=".4"/><ellipse cx="182" cy="91" rx="31" ry="66" fill="none" stroke="ACCENT" opacity=".3"/><path d="M116 91h132M125 62h114m-114 58h114" stroke="ACCENT" opacity=".3"/><rect x="58" y="62" width="88" height="63" rx="13" fill="#191D30" stroke="ACCENT"/><text x="86" y="104" fill="ACCENT" font-size="31" font-family="sans-serif">A</text><rect x="224" y="62" width="88" height="63" rx="13" fill="#191D30" stroke="ACCENT"/><text x="250" y="103" fill="ACCENT" font-size="28" font-family="sans-serif">文</text>',
        'Code helper':'<rect x="52" y="26" width="265" height="130" rx="14" fill="#ffffff" opacity=".05"/><circle cx="70" cy="42" r="3" fill="#F5A3C8"/><circle cx="82" cy="42" r="3" fill="#F6C578"/><circle cx="94" cy="42" r="3" fill="#7CE8C4"/><path d="M138 73l-21 19 21 19m92-38 21 19-21 19m-37-47-17 57" stroke="ACCENT" stroke-width="5" fill="none" stroke-linecap="round" stroke-linejoin="round"/>',
        'Interview coach':'<circle cx="127" cy="73" r="23" fill="ACCENT" opacity=".25"/><path d="M88 139c0-49 78-49 78 0" fill="ACCENT" opacity=".2"/><rect x="191" y="40" width="104" height="73" rx="16" fill="ACCENT" opacity=".18"/><path d="M209 62h65m-65 17h46" stroke="ACCENT" stroke-width="4" stroke-linecap="round"/><path d="M208 110v17l19-16" fill="ACCENT" opacity=".18"/>',
    }
    shape=designs.get(kind,designs['AI chat']).replace('ACCENT',color)
    return ('<svg xmlns="http://www.w3.org/2000/svg" width="370" height="180" viewBox="0 0 370 180">'
            '<defs><radialGradient id="glow"><stop stop-color="'+color+'" stop-opacity=".19"/>'
            '<stop offset="1" stop-color="#15182A" stop-opacity="0"/></radialGradient></defs>'
            '<rect width="370" height="180" rx="16" fill="#141727"/>'
            '<ellipse cx="190" cy="90" rx="185" ry="120" fill="url(#glow)"/>'+shape+'</svg>')


def brand():
    st.markdown('### :violet[✦] Bayaz Studio')
    st.caption('YOUR EVERYDAY CREATIVE WORKSPACE')


def privacy():
    with st.expander('Privacy & free usage'):
        st.write('Your prompts, recent chat and selected document text are sent to Groq. '
                 'Do not include passwords or sensitive personal information. '
                 'Conversations and projects stay in this browser session; download '
                 'anything you want to keep. No account database is connected.')
        st.write('Free-model limits apply. Answers and generated code need review. '
                 'The assistants do not browse the web or run your code.')
