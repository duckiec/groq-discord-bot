**wrote readme using ai cuz i hate documenting**

# Groq Discord Bot

A Discord bot that uses Groq's LLM API to provide AI chat capabilities in Discord servers.

## Features

- AI chat with conversation memory
- Per-server system message configuration
- Configurable conversation timeouts
- Command-based interface
- Conversation statistics
- Response caching for efficiency

## Setup

1. Clone this repository
2. Install dependencies:
```bash
pip install discord.py python-dotenv groq
```

3. Create a `.env` file with your credentials:
```bash
DISCORDKEY=your_discord_bot_token
GROQ=your_groq_api_key
```

4. Run the bot:
```bash
python main.py
```

## Commands

- `/ask [prompt]` - Ask the AI something
- `/status` - View your conversation stats
- `/system [message]` - Set AI system message (admin only)
- `/timeout [seconds]` - Set conversation timeout (admin only)
- `/help` - Show available commands

## Configuration

- Default conversation timeout: 60 seconds
- Maximum conversation history: 10 messages
- Response length limit: 1999 characters (Discord limit)

## Details
- Uses Groq's llama-3.3-70b-versatile model
- Implements request queuing and thread pooling
- Includes response caching (5-minute cache lifetime)
- Automatically cleans up inactive conversations

## Requirements/Libraries

- discord.py
- python-dotenv
- groq
