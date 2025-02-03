import os
from groq import Groq
from dotenv import load_dotenv
from collections import defaultdict
import time
import asyncio
from functools import lru_cache
import hashlib

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ"),
)

conversation_history = defaultdict(list)
last_activity = defaultdict(float)
system_messages = defaultdict(str)
timeouts = defaultdict(lambda: 60)
MAX_HISTORY = 10
request_queue = asyncio.Queue()

# Cache for identical requests within 5 minutes
@lru_cache(maxsize=1000, typed=True)
def get_cached_response(request_hash, timestamp):
    # Invalidate cache every 5 minutes
    if time.time() - timestamp > 300:
        get_cached_response.cache_clear()
        return None
    return None

def hash_request(messages):
    return hashlib.md5(str(messages).encode()).hexdigest()

async def process_request_queue():
    while True:
        if not request_queue.empty():
            request = await request_queue.get()
            await request
        await asyncio.sleep(0.1)

def cleanup_old_conversations():
    current_time = time.time()
    expired = [
        user_id for user_id, last_time in last_activity.items()
        if current_time - last_time > timeouts[user_id.split('-')[0]]
    ]
    for user_id in expired:
        del conversation_history[user_id]
        del last_activity[user_id]

def set_system_message(guild_id: str, message: str):
    system_messages[guild_id] = message

def set_timeout(guild_id: str, timeout: int):
    timeouts[guild_id] = timeout

def get_conversation_summary(user_id: str) -> str:
    if user_id not in conversation_history:
        return "No active conversation."
    
    msg_count = len(conversation_history[user_id])
    char_count = sum(len(msg["content"]) for msg in conversation_history[user_id])
    time_active = time.time() - last_activity[user_id]
    
    return f"Messages: {msg_count}\nTotal characters: {char_count}\nActive for: {int(time_active)}s"

def truncate_response(response: str, limit: int = 1999) -> str:
    if len(response) <= limit:
        return response
    
    # Try to cut at the last sentence
    last_period = response[:limit-3].rfind('.')
    if last_period > 0:
        return response[:last_period + 1] + "..."
    
    # If no sentence break found, just cut at limit
    return response[:limit-3] + "..."

async def getresponse(msg, author, guild_id):
    try:
        global client, conversation_history, last_activity
        user_id = f"{guild_id}-{author.id}"
        
        last_activity[user_id] = time.time()
        asyncio.create_task(asyncio.to_thread(cleanup_old_conversations))
        
        messages = []
        if system_messages[guild_id]:
            messages.append({"role": "system", "content": system_messages[guild_id]})
        
        messages.extend(conversation_history[user_id])
        messages.append({"role": "user", "content": f"{msg} (RESPOND IN LESS THAN 1999 CHARACTERS)"})
        
        if len(messages) > MAX_HISTORY:
            messages = messages[-MAX_HISTORY:]
        
        conversation_history[user_id] = messages
        
        request_hash = hash_request(messages)
        cached_response = get_cached_response(request_hash, time.time())
        if cached_response:
            return cached_response
        
        if not client:
            raise Exception("API client not initialized")
            
        chat_completion = await asyncio.to_thread(
            client.chat.completions.create,
            messages=messages,
            model="llama-3.3-70b-versatile",
        )
        
        if not chat_completion or not chat_completion.choices:
            raise Exception("No response received from API")
            
        response = chat_completion.choices[0].message.content[:1999]
        conversation_history[user_id].append({"role": "assistant", "content": response})
        
        get_cached_response(request_hash, time.time())
        
        return response
        
    except Exception as e:
        print(f"Error in getresponse: {str(e)}")
        return f"Sorry, I encountered an error: {str(e)}"

# Pre-initialize cache
get_cached_response(None, 0)

