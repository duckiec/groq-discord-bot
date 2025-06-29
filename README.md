**Groq Discord Bot**

AI chatbot for Discord using Groq API.
Features

    remembers convo

    set system prompt

    timeout config

    basic stats

    response cache

Setup

pip install discord.py python-dotenv groq

make a .env:

DISCORDKEY=your_discord_token
GROQ=your_groq_key

run with:

python main.py

Commands

    /ask – ask stuff

    /status – see usage

    /system – set system prompt (admin)

    /timeout – set convo timeout (admin)

    /help – help

Notes

    llama3-70b via Groq

    10-message memory

    60s default timeout

    5-min reply cache

    1999 char limit (Discord)
