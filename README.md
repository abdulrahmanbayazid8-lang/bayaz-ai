# Bayaz AI - hosted chat app

A Streamlit chat app using Groq for cloud inference. It does not require Ollama or the owner's laptop to remain online.

## Features

Streaming responses, bounded recent conversation context, a new-chat button, chat downloads, and optional PDF questions with retrieved page evidence. This hosted version deliberately uses keyword PDF retrieval instead of the local app's EmbeddingGemma search. It has no agent tool execution or web browsing. Conversations are session-only; there are no user accounts or saved chat databases.

## Publish on Streamlit Community Cloud

1. Create a Groq account and API key at https://console.groq.com/keys . Keep the key private.
2. Use the Groq Free plan only. Do not add a payment method or upgrade to a paid tier. Requests are subject to the free account model and usage limits; if the quota is exhausted, the app must wait for it to reset. If signup requires payment, stop and choose another provider. Billing caps mentioned below apply only if the owner later explicitly chooses paid service.
3. Create a GitHub repository and upload this folder's contents. Upload `app.py`, `requirements.txt`, `.gitignore`, `.streamlit/config.toml`, this README and the example secrets file. Never upload actual secrets.
4. At https://share.streamlit.io/ choose Create app, select the repository and set the entrypoint to `app.py`.
5. In Advanced settings, choose a supported Python release (3.12 is a suitable starting point). In Secrets, enter GROQ_API_KEY, GROQ_MODEL and DAILY_REQUEST_LIMIT using the template's TOML format, with the real API key. These are server-side secrets, not repository files.
6. Deploy, test the cloud connection, and use the hosting dashboard's app sharing settings to allow the intended public audience.
7. Test two simultaneous browser sessions to check history separation. Verify New chat, downloads, rate-limit messages, an unreadable PDF, missing evidence, and model-service failures before sharing broadly.

## Budget controls

Defaults: 100 requests per UTC day per running app process, 20 requests per hour per browser session, 10 seconds between submissions and 1,024 maximum completion tokens per request. These are traffic controls, not a guaranteed currency cap. They reset when the process or session restarts and do not coordinate across multiple server instances. The provider's organization-level enforced spending cap is required for a hard budget boundary. Requests that fail after reservation still count toward the application's daily allowance.

## Data and limitations

Messages, recent history and selected PDF passages leave the hosting server for Groq. Follow the provider's data policies. This app does not intentionally log message contents or write chats/PDFs to a database, but hosting and inference vendors have their own handling policies. PDF text stays in the session's memory; no globally cached PDF data is used. PDF parsing of untrusted files and keyword retrieval have limitations. No OCR, semantic search, per-user authentication, persistent quotas, paid subscriptions or uptime guarantee is included. Streamlit Community Cloud can sleep or hit resource limits. This is an initial publishable release, not a high-availability commercial service.

## Verification status

Core code can be checked with mocked API streaming, retrieval, context and traffic-limit tests. A real cloud API request and deployed UI smoke test still require the owner's API key and hosting account. Do not claim live deployment until the provider returns a working public URL.

## References

- https://console.groq.com/docs/models
- https://console.groq.com/docs/spend-limits
- https://console.groq.com/docs/api-reference
- https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy
