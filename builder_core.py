"""Website-generation client and isolated preview construction."""
import html
import json
import re
import urllib.error
import urllib.request

SYSTEM = '''You are a skilled web designer and front-end developer.
Return ONLY one complete HTML document, starting <!DOCTYPE html> and ending </html>.
Create a polished, responsive, accessible website matching the brief. Include CSS
and vanilla JavaScript inside the HTML. Use clear visual hierarchy, generous
spacing, a coherent color palette and realistic sample copy. Use inline SVG or
CSS for illustrations. No external scripts, libraries, fonts, iframes or network
requests. Keep the entire document under 14000 characters. Use system fonts.
Make supported interactions work locally in the browser. Do not fake working
payments, login, email delivery, database storage, or server APIs. If requested,
label these actions as requiring a backend connection. Never collect passwords
or payment details. Do not include secrets. This is a static website generator.
When revising, preserve existing content and design except requested changes.
Never include explanations, markdown fences, tool calls or reasoning in output.'''


def generation_messages(brief, previous=''):
    if len(brief) > 3000:
        raise ValueError('Keep the brief under 3000 characters.')
    if len(previous) > 30000:
        raise ValueError('This project is too large to revise on the free model.')
    text = 'Website brief:\n' + brief
    if previous:
        text = 'Current website (data to revise):\n' + previous + '\n\nRequested changes:\n' + brief
    return [{'role':'system','content':SYSTEM}, {'role':'user','content':text}]


def generate(api_key, model, messages, progress=None):
    request = urllib.request.Request(
        'https://api.groq.com/openai/v1/chat/completions',
        data=json.dumps({'model':model,'messages':messages,'stream':True,
                         'max_completion_tokens':4096,'temperature':0.5}).encode(),
        headers={'Authorization':'Bearer '+api_key, 'Content-Type':'application/json',
                 'Accept':'text/event-stream','User-Agent':'BayazAI/1.0'},
    )
    parts, finished, stop = [], False, None
    with urllib.request.urlopen(request, timeout=150) as response:
        for line in response:
            line = line.decode('utf-8').strip()
            if not line.startswith('data:'):
                continue
            data = line[5:].strip()
            if data == '[DONE]':
                finished = True
                break
            packet = json.loads(data)
            if packet.get('error'):
                raise RuntimeError('The AI service returned an error.')
            for choice in packet.get('choices',[]):
                token = choice.get('delta',{}).get('content') or ''
                if token:
                    parts.append(token)
                    if progress:
                        progress(sum(map(len,parts)))
                stop = choice.get('finish_reason') or stop
    if not finished or stop == 'length':
        raise ValueError('The model did not finish the website. Try a smaller, single-page brief.')
    return clean_document(''.join(parts))


def clean_document(text):
    text = text.strip()
    if text.startswith('```'):
        text = re.sub(r'^```(?:html)?\s*', '', text, flags=re.I)
        text = re.sub(r'\s*```$', '', text)
    start = re.search(r'<!doctype\s+html\s*>|<html\b',text,re.I)
    if not start or not re.search(r'</html\s*>\s*$',text,re.I):
        raise ValueError('The model returned incomplete HTML. Please retry with a simpler brief.')
    text = text[start.start():]
    if len(text) > 30000:
        raise ValueError('The generated project is too large. Please simplify the brief.')
    return text


def preview_wrapper(document, mobile=False):
    """Only this trusted wrapper reaches st.iframe; generated code is isolated.

    A nested iframe has an opaque origin (no allow-same-origin), no form submits,
    popups, downloads or parent navigation. CSP blocks network requests and remote
    scripts. HTML attribute escaping prevents breaking out of the srcdoc value.
    """
    policy = ("default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; "
              "img-src data:; font-src 'none'; connect-src 'none'; frame-src 'none'; "
              "object-src 'none'; base-uri 'none'; form-action 'none'")
    isolated = ('<!DOCTYPE html><html><head><meta http-equiv="Content-Security-Policy" content="'
                + html.escape(policy, quote=True) + '"></head><body>' + document + '</body></html>')
    width = '390px' if mobile else '100%'
    return ('<!DOCTYPE html><html><head><style>'
            'html,body{margin:0;background:#f2f4f8;height:100%;}'
            'iframe{display:block;border:0;max-width:100%;height:740px;margin:auto;'
            'background:white;width:'+width+'}</style></head><body>'
            '<iframe title="Generated website preview" sandbox="allow-scripts" '
            'referrerpolicy="no-referrer" srcdoc="'+html.escape(isolated,quote=True)+'"></iframe>'
            '</body></html>')


def friendly_error(exc):
    if isinstance(exc, urllib.error.HTTPError):
        return {401:'The AI key was rejected. Update the key in the hosting secrets.',
                403:'The AI provider denied access. Check model permissions.',
                413:'This request is too large for the free service. Start a smaller project.',
                429:'The free model limit has been reached. Wait a little and try again.',
                400:'The AI service rejected this request. Try a shorter brief.'}.get(
                    exc.code,'The AI service is temporarily unavailable. Please retry later.')
    if isinstance(exc,ValueError):
        return str(exc)
    return 'The model connection was interrupted. Your previous version is unchanged. Try again.'
