import os
import asyncio
import feedparser
from typing import List, Dict, Any, Optional
import streamlit as st
import re
import time
import warnings
import logging
from datetime import date, datetime, timedelta
from dotenv import load_dotenv

# Try importing Google ADK components with error handling
try:
    from google.adk.agents import Agent
    from google.adk.sessions import InMemorySessionService
    from google.adk.runners import Runner
    from google.adk.tools.tool_context import ToolContext
    from google.genai import types as genai_types
    ADK_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Google ADK not available: {e}")
    print("Please install the Google ADK library or use the fallback implementation")
    ADK_AVAILABLE = False

# --- Configuration ---
load_dotenv()
warnings.filterwarnings("ignore")
logging.basicConfig(level=logging.ERROR)

# --- Constants ---
NEWS_ITEMS_PRESENTED_STATE_KEY = "last_presented_news_items"
NEWS_FETCH_CACHE_STATE_KEY = "fetched_news_bbc_npr_cache"
DEFAULT_FEED_URLS = [
    "https://feeds.bbci.co.uk/news/rss.xml",
    "https://feeds.npr.org/1001/rss.xml"
]
MAX_ITEMS_TO_PROCESS = 200
MODEL_GEMINI = "gemini-2.0-flash"  # Using a more recent model
APP_NAME_FOR_ADK = "news_agent_final_mem_v3" # Incremented version
USER_ID = "streamlit_user_sf_final_mem_v3"

print("✅ Imports and Configuration Loaded.")

# --------------------------------------------------------------------------
# Fallback Implementation (when ADK is not available)
# --------------------------------------------------------------------------

class FallbackToolContext:
    """Fallback tool context for when ADK is not available"""
    def __init__(self):
        self.state = {}

def fetch_news_fallback(target_date_str: Optional[str] = None) -> Dict[str, Any]:
    """
    Fallback news fetching function that works without ADK
    """
    print(f"--- Fallback: fetch_news called with target_date_str: {target_date_str} ---")
    
    today = date.today()
    if target_date_str:
        target_date_str_lower = target_date_str.lower()
        if target_date_str_lower == "today":
            target_date = today
        elif target_date_str_lower == "yesterday":
            target_date = today - timedelta(days=1)
        else:
            try:
                target_date = datetime.strptime(target_date_str, "%Y-%m-%d").date()
                if (today - target_date).days > 14:
                    return {
                        "status": "error", 
                        "message": "Sorry, I can only retrieve news from the past two weeks."
                    }
            except ValueError:
                return {
                    "status": "error", 
                    "message": f"Invalid date format: {target_date_str}. Use YYYY-MM-DD, 'today', or 'yesterday'."
                }
    else:
        target_date = None  # Will use date range
    
    all_items = []
    errors = []
    
    for url in DEFAULT_FEED_URLS:
        try:
            print(f"--- Fallback: Fetching from {url} ---")
            feed = feedparser.parse(url)
            
            if feed.status >= 400:
                errors.append(f"HTTP {feed.status} for {url}")
                continue
                
            for entry in feed.entries[:50]:  # Limit entries per feed
                if not (hasattr(entry, 'title') and hasattr(entry, 'link')):
                    continue
                    
                pub_struct = getattr(entry, 'published_parsed', None) or getattr(entry, 'updated_parsed', None)
                if pub_struct:
                    try:
                        entry_date = date(pub_struct.tm_year, pub_struct.tm_mon, pub_struct.tm_mday)
                        
                        if target_date:
                            if entry_date != target_date:
                                continue
                        else:
                            # Default: last 7 days
                            if (today - entry_date).days > 7:
                                continue
                    except (ValueError, AttributeError):
                        continue
                
                description = getattr(entry, 'description', '')
                description = re.sub('<[^<]+?>', '', description).strip()
                
                source = "BBC News" if "bbc" in url.lower() else "NPR News"
                
                item = {
                    "title": entry.title,
                    "link": entry.link,
                    "description": description,
                    "published_str": getattr(entry, 'published', ''),
                    "source": source
                }
                all_items.append(item)
                
        except Exception as e:
            errors.append(f"Error fetching {url}: {str(e)}")
            print(f"--- Fallback: Error fetching {url}: {e} ---")
    
    if all_items:
        return {"status": "success", "items": all_items}
    elif errors:
        return {"status": "error", "message": f"Errors occurred: {'; '.join(errors)}"}
    else:
        return {"status": "error", "message": "No news items found for the specified criteria."}

# --------------------------------------------------------------------------
# ADK Implementation (when available)
# --------------------------------------------------------------------------

if ADK_AVAILABLE:
    def fetch_and_return_news(tool_context: ToolContext, target_date_str: Optional[str] = None) -> Dict[str, Any]:
        """
        ADK version of news fetching with session state management
        """
        print(f"--- ADK Tool: fetch_and_return_news called with target_date_str: {target_date_str} ---")
        
        today = date.today()
        single_day = None
        date_start = None
        date_end = None
        
        if target_date_str:
            target_date_str_lower = target_date_str.lower()
            if target_date_str_lower == "today":
                single_day = today
            elif target_date_str_lower == "yesterday":
                single_day = today - timedelta(days=1)
            else:
                try:
                    parsed_date = datetime.strptime(target_date_str, "%Y-%m-%d").date()
                    if (today - parsed_date).days > 14:
                        if NEWS_ITEMS_PRESENTED_STATE_KEY in tool_context.state:
                            del tool_context.state[NEWS_ITEMS_PRESENTED_STATE_KEY]
                        return {
                            "status": "error", 
                            "message": "Sorry, I can only retrieve news from the past two weeks."
                        }
                    single_day = parsed_date
                except ValueError:
                    if NEWS_ITEMS_PRESENTED_STATE_KEY in tool_context.state:
                        del tool_context.state[NEWS_ITEMS_PRESENTED_STATE_KEY]
                    return {
                        "status": "error", 
                        "message": f"Invalid date format: {target_date_str}. Use YYYY-MM-DD, 'today', or 'yesterday'."
                    }
        else:
            date_end = today
            date_start = today - timedelta(days=7)
        
        if (NEWS_FETCH_CACHE_STATE_KEY not in tool_context.state or 
            not isinstance(tool_context.state.get(NEWS_FETCH_CACHE_STATE_KEY), dict)):
            tool_context.state[NEWS_FETCH_CACHE_STATE_KEY] = {'items': [], 'cache': {}}
        
        fetch_state = tool_context.state[NEWS_FETCH_CACHE_STATE_KEY]
        if 'cache' not in fetch_state: fetch_state['cache'] = {}
        if 'items' not in fetch_state: fetch_state['items'] = []
        
        all_items = []
        errors = []
        
        for url in DEFAULT_FEED_URLS:
            try:
                feed_cache = fetch_state['cache'].get(url, {})
                etag = feed_cache.get('etag')
                modified = feed_cache.get('modified')
                
                feed = feedparser.parse(url, etag=etag, modified=modified)
                
                if feed.status == 304:
                    cached_items = [item for item in fetch_state.get('items', []) if item.get('source_feed') == url]
                    all_items.extend(cached_items)
                    continue
                elif feed.status >= 400:
                    errors.append(f"HTTP {feed.status} for {url}")
                    continue
                
                if hasattr(feed, 'etag') and feed.etag: fetch_state['cache'].setdefault(url, {})['etag'] = feed.etag
                if hasattr(feed, 'modified') and feed.modified: fetch_state['cache'].setdefault(url, {})['modified'] = feed.modified
                
                for entry in feed.entries:
                    if len(all_items) >= MAX_ITEMS_TO_PROCESS: break
                    if not (hasattr(entry, 'title') and hasattr(entry, 'link')): continue
                    
                    pub_struct = (getattr(entry, 'published_parsed', None) or getattr(entry, 'updated_parsed', None))
                    description = getattr(entry, 'description', '')
                    description = re.sub('<[^<]+?>', '', description).strip()
                    
                    item = {
                        "title": entry.title, "link": entry.link, "description": description,
                        "published_str": getattr(entry, 'published', ''), "source_feed": url,
                        "published_or_updated_struct": pub_struct
                    }
                    all_items.append(item)
                    
            except Exception as e:
                errors.append(f"Error processing {url}: {str(e)}")
        
        filtered_items = []
        for item in all_items:
            struct_to_check = item.get("published_or_updated_struct")
            if struct_to_check:
                try:
                    item_date = date(struct_to_check.tm_year, struct_to_check.tm_mon, struct_to_check.tm_mday)
                    
                    if single_day:
                        if item_date == single_day:
                            item.pop("published_or_updated_struct", None)
                            filtered_items.append(item)
                    elif date_start and date_end:
                        if date_start <= item_date <= date_end:
                            item.pop("published_or_updated_struct", None)
                            filtered_items.append(item)
                except (ValueError, AttributeError, TypeError):
                    pass
        
        fetch_state['items'] = all_items
        
        if filtered_items:
            tool_context.state[NEWS_ITEMS_PRESENTED_STATE_KEY] = filtered_items
            return {"status": "success", "items": filtered_items}
        else:
            if NEWS_ITEMS_PRESENTED_STATE_KEY in tool_context.state:
                del tool_context.state[NEWS_ITEMS_PRESENTED_STATE_KEY]
            
            if errors: return {"status": "error", "message": f"Errors occurred: {'; '.join(errors)}"}
            else: return {"status": "error", "message": "No news items found for the specified criteria."}

    root_agent = Agent(
        name="news_and_chat_agent_final_mem_v3",
        model=MODEL_GEMINI,
        description="A helpful assistant that provides news briefings and can answer follow-up questions.",
        instruction=(
            "You are a News & Chat Assistant. Analyze the user's message to determine intent:\n\n"
            "1. **New News Briefing**: Keywords like 'news', 'headlines', 'briefing' with optional dates\n"
            "   - MUST call fetch_and_return_news tool\n"
            "   - Pass target_date_str if specified ('today', 'yesterday', 'YYYY-MM-DD')\n"
            "   - Present all items with clear formatting\n\n"
            "2. **Follow-up Questions**: References to previously presented news\n"
            "   - DO NOT call tools\n"
            "   - Use session state 'last_presented_news_items' to answer\n"
            "   - If state is empty, say you don't have previous briefing details\n\n"
            "3. **General Chat**: Everything else\n"
            "   - DO NOT call tools\n"
            "   - Respond conversationally\n\n"
            "Format news items using Markdown with title, source, and description."
        ),
        tools=[fetch_and_return_news]
    )

    def get_session_service():
        """
        Gets or creates the InMemorySessionService from st.session_state.
        This is the most reliable way to persist state in Streamlit.
        """
        if 'session_service' not in st.session_state:
            print("--- Creating new InMemorySessionService and storing in st.session_state ---")
            st.session_state.session_service = InMemorySessionService()
        return st.session_state.session_service

    def get_session_id():
        """Get or create a unique session ID stored in st.session_state."""
        session_id_key = 'adk_session_id_v3'
        if session_id_key not in st.session_state:
            timestamp = int(time.time())
            random_hex = os.urandom(4).hex()
            st.session_state[session_id_key] = f"st_session_{timestamp}_{random_hex}"
            print(f"Created new ADK session ID: {st.session_state[session_id_key]}")
        return st.session_state[session_id_key]

    async def run_adk_async(user_message_text: str) -> str:
        """
        Runs the ADK agent asynchronously using a persistent session service.
        """
        session_service = get_session_service()
        session_id = get_session_id()

        runner = Runner(
            agent=root_agent,
            app_name=APP_NAME_FOR_ADK,
            session_service=session_service
        )
        
        print(f"--- Running ADK with session: {session_id} ---")
        
        content = genai_types.Content(
            role='user',
            parts=[genai_types.Part(text=user_message_text)]
        )
        
        final_response_text = "The agent encountered an issue processing your request."
        
        try:
            async for event in runner.run_async(
                user_id=USER_ID, 
                session_id=session_id, 
                new_message=content
            ):
                if event.is_final_response():
                    if event.content and event.content.parts and hasattr(event.content.parts[0], 'text'):
                        final_response_text = event.content.parts[0].text
                    break
        except Exception as e:
            print(f"ADK execution error: {e}")
            if "not found" in str(e).lower():
                final_response_text = "There was a session issue. Please try your request again. If the problem persists, try resetting the session."
            else:
                final_response_text = f"Error processing request: {e}"
        
        return final_response_text

# --------------------------------------------------------------------------
# Streamlit UI
# --------------------------------------------------------------------------

def format_news_response(result: Dict[str, Any]) -> str:
    """Format news response for display"""
    if result["status"] == "error":
        return f"❌ {result['message']}"
    
    items = result.get("items", [])
    if not items:
        return "📰 No news items found for your request."
    
    response = f"📰 **Found {len(items)} news items:**\n\n"
    
    for i, item in enumerate(items, 1):
        title = item.get("title", "No title")
        link = item.get("link", "#")
        description = item.get("description", "No description available")
        source = item.get("source", "Unknown source")
        published = item.get("published_str", "")
        
        if source == "Unknown source" and "source_feed" in item:
            source = "BBC News" if "bbc" in item["source_feed"].lower() else "NPR News"
        
        response += f"### {i}. [{title}]({link})\n"
        response += f"**Source:** {source}\n"
        if published:
            response += f"**Published:** {published}\n"
        response += f"\n{description}\n\n---\n\n"
    
    return response

def main():
    st.set_page_config(
        page_title="News & Chat Agent",
        layout="wide",
        initial_sidebar_state="auto"
    )
    
    st.title("📰 News & Chat Assistant")
    st.markdown("""
    Ask for news from BBC/NPR or just chat!
    
    **Examples:**
    - `latest news` (past 7 days)
    - `news from today` or `news from yesterday`
    - `news from 2025-06-10` (specific date)
    - Follow-up questions about recent news
    """)
    
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key or "YOUR_GOOGLE_API_KEY" in api_key:
        st.error("""
        🚨 **Google API Key Required!**
        
        1. Create a `.env` file with: `GOOGLE_API_KEY='your_actual_key'`
        2. Get your key from Google AI Studio
        3. Restart the application
        """)
        st.stop()
    
    use_adk = False
    if ADK_AVAILABLE:
        try:
            get_session_service()
            session_id = get_session_id()
            st.sidebar.success(f"✅ ADK Initialized\nSession: ...{session_id[-12:]}")
            use_adk = True
        except Exception as e:
            st.sidebar.error(f"❌ ADK Init Error: {e}")
            st.sidebar.info("Using fallback mode")
            use_adk = False
    else:
        st.sidebar.warning("⚠️ ADK not available - using fallback mode")
        use_adk = False
    
    message_history_key = "messages_v3"
    if message_history_key not in st.session_state:
        st.session_state[message_history_key] = []
    
    for message in st.session_state[message_history_key]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"], unsafe_allow_html=False)
    
    if prompt := st.chat_input("Ask for news or just chat..."):
        st.session_state[message_history_key].append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = ""
                try:
                    if use_adk:
                        response = asyncio.run(run_adk_async(prompt))
                    else:
                        if any(keyword in prompt.lower() for keyword in ['news', 'headlines', 'briefing']):
                            target_date = None
                            if 'today' in prompt.lower(): target_date = 'today'
                            elif 'yesterday' in prompt.lower(): target_date = 'yesterday'
                            else:
                                date_match = re.search(r'\d{4}-\d{2}-\d{2}', prompt)
                                if date_match: target_date = date_match.group()
                            
                            result = fetch_news_fallback(target_date)
                            response = format_news_response(result)
                        else:
                            response = "I'm a news assistant! Ask me for news with phrases like 'latest news', 'news from today', or just chat with me."
                    
                    st.markdown(response)
                    
                except Exception as e:
                    error_msg = f"Sorry, a critical error occurred: {e}"
                    st.error(error_msg)
                    response = error_msg
        
        st.session_state[message_history_key].append({"role": "assistant", "content": response})
    
    st.sidebar.divider()
    st.sidebar.header("System Info")
    st.sidebar.caption(f"**Mode:** {'ADK' if use_adk else 'Fallback'}")
    st.sidebar.caption(f"**Model:** {MODEL_GEMINI}")
    
    if use_adk:
        st.sidebar.divider()
        st.sidebar.header("Session Management")
        if st.sidebar.button("Reset Session"):
            keys_to_delete = [
                'adk_session_id_v3',
                'session_service',
                'messages_v3'
            ]
            for key in keys_to_delete:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()

if __name__ == "__main__":
    main()