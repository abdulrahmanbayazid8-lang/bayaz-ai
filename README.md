# Bayaz Studio

## AI workspace

The home page offers six focused assistants: general chat, writing, summarizing, translation, coding help and interview practice. Each tool uses its own instructions and conversation thread. Tone controls, ten translation languages, PDF/TXT source documents, prompt starters and conversation downloads are available. Sources and recent context are bounded to fit the free model. These assistants generate text; they do not browse, execute code, send emails or generate images. Long-document summaries use the opening excerpt and say so. Conversations are session-only, not saved across visits.

The interface uses an original dark violet theme, native Streamlit components and original vector artwork.

An AI website builder and chat application, built with Python, Streamlit and Groq.

## Website builder

Describe a website, generate a single HTML file with inline CSS and JavaScript, preview desktop/mobile layouts, request revisions and download HTML or a ZIP. Up to five projects and five versions per project remain in the current browser session. Download before leaving; there is no account database or permanent project storage.

The design is inspired by prompt-first app builders, with original Bayaz branding. This is a single-page website generator, not a full-stack hosting platform. Payments, authentication, email delivery and database features require separate backend services. Generated projects are not automatically deployed.

## Preview isolation

Only a trusted wrapper is passed to Streamlit's iframe API. Generated content is attribute-escaped into a nested sandboxed iframe with an opaque origin (no allow-same-origin), no form submission, popups, downloads or top navigation. A Content Security Policy blocks outbound connections, external scripts and remote assets. The downloaded HTML is the original generated code: review it before running or publishing.

## Run

Install requirements, configure Streamlit secrets privately, then run `streamlit run app.py`.

Required secret: GROQ_API_KEY. Optional: GROQ_MODEL (default openai/gpt-oss-20b), DAILY_BUILD_LIMIT (default 40), DAILY_REQUEST_LIMIT (chat mode, default 100).

Use the provider's Free plan only. Do not add payment details. Provider quotas can interrupt availability. Model availability and free limits may change.

## Publish

Deploy this repository on Streamlit Community Cloud, entrypoint app.py, Python 3.12. Configure the real API key only in the hosting dashboard's Secrets field. Never put keys in code, repository descriptions, commits or public files. A previously exposed key must be revoked.

## Traffic controls

Builder requests have a per-process daily allowance and a per-session 10/hour allowance, with at least 15 seconds between builds. Chat mode has separate traffic limits. These reset on restarts and do not prevent all abuse or coordinate across replicas. No paid subscription functionality or uptime guarantee is included.

## Testing and limitations

Core checks cover complete HTML validation, interrupted streaming, output limits, preview sandbox attributes and escaping. Live tests must also verify generation, revisions, preview, downloads and the deployed model connection. Prompts and current website source are sent to Groq. This app does not intentionally save projects or chats to a database. Providers have their own data policies. Generated code and AI answers may contain errors.
