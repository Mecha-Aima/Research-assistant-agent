import streamlit as st
import time
import uuid
import os
from typing import Any
import random

from graph import run_query_with_history
from utils import extract_thinking, format_markdown_safely


st.set_page_config(
    page_title="AI Research Assistant",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)


st.markdown("""
<style>
    .main {
        padding: 2rem;
    }
    
    .thinking-text {
        font-size: 0.85rem;
        color: #FAF9F6;
        background-color: #f8f9fa;
        padding: 12px;
        border-radius: 8px;
        border-left: 3px solid #6c757d;
        margin: 10px 0 15px 20px;
        max-height: 300px;
        overflow-y: auto;
    }
    
    
    .chat-message {
        display: flex;
        margin-bottom: 15px;   
    }
    
    
    .user-message {
        background-color: #383d4e;
        padding: 12px 16px;
        border-radius: 15px 15px 2px 15px;
        margin-left: auto;
        margin-right: 10px;
        max-width: 80%;
        box-shadow: 0 1px 2px rgba(0,0,0,0.1);
        color: white;
    }
    
    
    .agent-message {
        background-color: #f8f9fa;
        padding: 12px 16px;
        border-radius: 15px 15px 15px 2px;
        margin-right: auto;
        margin-left: 10px;
        max-width: 80%;
        box-shadow: 0 1px 2px rgba(0,0,0,0.1);
        color: black;
    }
    
    
    .agent-icon {
        background-color: #6495ED;
        color: white;
        width: 40px;
        height: 40px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.3rem;
        margin-right: 10px;
    }
    
    .user-icon {
        background-color: #7EB77F;
        color: white;
        width: 40px;
        height: 40px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.3rem;
        margin-left: 10px;
    }
    
    
    @keyframes pulse {
        0% {
            transform: scale(0.95);
            opacity: 0.7;
        }
        50% {
            transform: scale(1);
            opacity: 1;
        }
        100% {
            transform: scale(0.95);
            opacity: 0.7;
        }
    }
    
    .loading-icon {
        animation: pulse 1.5s infinite ease-in-out;
    }
    
    
    .markdown-content {
        line-height: 1.6;
    }
    
    .markdown-content h1, .markdown-content h2, .markdown-content h3 {
        margin-top: 1em;
        margin-bottom: 0.5em;
    }
    
    .markdown-content p {
        margin-bottom: 1em;
    }
    
    .markdown-content ul, .markdown-content ol {
        margin-bottom: 1em;
        margin-left: 1.5em;
    }
    
    .markdown-content code {
        font-family: monospace;
        background-color: #36454F ;
        padding: 2px 4px;
        border-radius: 3px;
    }
    
    .markdown-content pre {
        background-color: #f8f8f8;
        padding: 10px;
        border-radius: 5px;
        overflow-x: auto;
    }
    
    
    .tool-card {
        background-color: rgba(54, 69, 79, 0.50);
        border-radius: 10px;
        padding: 15px;
        margin: 10px 5px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        transition: transform 0.2s, box-shadow 0.2s;
        color: #FAF9F6;
    }
    
    .tool-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    }
    
    
    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
    .main, .block-container {
    padding-bottom: 140px; 
}
    
    .input-area {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        background-color: white;
        padding: 20px; 
        box-shadow: 0 -2px 10px rgba(0,0,0,0.1);
        z-index: 1000;
        border-top: 1px solid #e0e0e0; 
    }

    .chat-container {
        margin-bottom: 100px; 
        padding-bottom: 30px;
    }
    
    .stTextInput > div > div > input {
        border-radius: 20px;
        padding: 10px 15px;
        border: 1px solid #e0e0e0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }

    .stTextInput > div > div > input:focus {
        border-color: #2ecc71;
        box-shadow: 0 1px 3px rgba(76,175,80,0.2);
    }
    
    
    div.stButton > button {
        background-color: #4CAF50;
        color: white;
        border-radius: 20px;
        padding: 5px 15px;
        font-weight: bold;
        border: none;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
    }
    
    div.stButton > button:hover {
        background-color: #45a049;
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        color: white;
    }
    
    footer {
        visibility: hidden;
    }
</style>
""", unsafe_allow_html=True)


if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'thread_id' not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

if 'thinking' not in st.session_state:
    st.session_state.thinking = False

if 'current_tool' not in st.session_state:
    st.session_state.current_tool = None

if 'used_tools' not in st.session_state:
    st.session_state.used_tools = set()

if 'input_value' not in st.session_state:
    st.session_state.input_value = ""


def get_thinking_message(tools_used):
    """
    Get a human-readable message for the tools being used.
    
    Args:
        tools_used: List of tools being used
        
    Returns:
        A human-readable message
    """
    tool_messages = {
        'arxiv': '📑 Searching through research papers...',
        'wikipedia': '🌐 Looking through Wikipedia articles...',
        'tavily_search_results_json': '🔎 Searching the web...'
    }
    
    if st.session_state.current_tool:
        return tool_messages.get(st.session_state.current_tool, '🧠 Processing your request...')
    
    if tools_used:
        first_tool = tools_used[0]
        return tool_messages.get(first_tool, '🧠 Processing your request...')
    
    # Default thinking message
    return '🧠 Thinking about your question...'


def stream_response(response):
    """
    Simulate streaming effect for the agent's response.
    
    Args:
        response: The response to stream
    """
    placeholder = st.empty()
    thinking, cleaned_response = extract_thinking(response)
    
    st.session_state.thinking = False
    
    displayed_text = ""
    for i in range(len(cleaned_response)):
        displayed_text += cleaned_response[i]
        placeholder.markdown(f"""
        <div class="chat-message">
            <div class="agent-icon">🤖</div>
            <div class="agent-message">
                <div class="markdown-content">{displayed_text}▌</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        time.sleep(random.uniform(0.01, 0.03))
    
    placeholder.markdown(f"""
    <div class="chat-message">
        <div class="agent-icon">🤖</div>
        <div class="agent-message">
            <div class="markdown-content">{cleaned_response}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Display thinking if available
    if thinking:
        st.markdown(f"""
        <div class="thinking-text">
            <strong>Thinking process:</strong><br>{thinking}
        </div>
        """, unsafe_allow_html=True)
    
    return thinking, cleaned_response


def process_query(user_query):
    """
    Process the user query and get the agent response.
    
    Args:
        user_query: The user's query
        
    Returns:
        The agent's response
    """
    st.session_state.thinking = True
    
    try:
        response = run_query_with_history(st.session_state.messages, st.session_state.thread_id)
        
        if response and 'messages' in response and response['messages']:
            # Get the last message from the agent
            agent_message = response['messages'][-1]
            agent_response = agent_message.content
            
            # Process the response to extract thinking
            thinking, _ = extract_thinking(agent_response)
            
            # Get tools used from the response
            tools_used = response.get('tools_used', [])
            
            # Set current tool if any tools were used
            st.session_state.current_tool = tools_used[0] if tools_used else None
            
            # Add agent message to history
            st.session_state.messages.append({
                "role": "assistant",
                "content": agent_response,
                "thinking": thinking,
                "used_tools": tools_used
            })
            
            return agent_response
        else:
            error_msg = "I couldn't generate a response. Please try again."
            
            # Add error message to history
            st.session_state.messages.append({
                "role": "assistant",
                "content": error_msg
            })
            
            return error_msg
    
    except Exception as e:
        error_msg = f"An error occurred: {str(e)}"
        
        # Add error message to history
        st.session_state.messages.append({
            "role": "assistant",
            "content": error_msg
        })
        
        return error_msg
    finally:
        st.session_state.thinking = False
        st.session_state.current_tool = None


with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/artificial-intelligence.png", width=80)
    st.title("AI Research Assistant")
    
    st.markdown("### Powered by")
    st.markdown("- **LangGraph** - Agent orchestration")
    st.markdown("- **Groq** - LLM provider (Qwen-QWQ-32B)")
    
    st.markdown("### Available Tools")
    
    tool_cards = [
        {"emoji": "📑", "title": "ArXiv", "desc": "Scientific papers"},
        {"emoji": "🌐", "title": "Wikipedia", "desc": "Knowledge base"},
        {"emoji": "🔎", "title": "Tavily", "desc": "Web search"},
        {"emoji": "🧠", "title": "Concepts", "desc": "AI reasoning"}
    ]

    rows = [tool_cards[i:i+2] for i in range(0, len(tool_cards), 2)]

    for row in rows:
        cols = st.columns(2)
        for col, tool in zip(cols, row):
            with col:
                st.markdown(f"""
                <div class="tool-card" style="text-align: center;">
                    <h4>{tool['emoji']} {tool['title']}</h4>
                    <p style="font-size: 0.8rem;">{tool['desc']}</p>
                </div>
                """, unsafe_allow_html=True)
        
    st.divider()
    
    st.subheader("⚙️ Settings")
    
    # Clear conversation button
    if st.button("🗑️ Clear Conversation"):
        st.session_state.messages = []
        st.session_state.thread_id = str(uuid.uuid4())
        st.rerun()
    
    # Check API keys
    tavily_key = os.getenv("TAVILY_API_KEY")
    groq_key = os.getenv("GROQ_API_KEY")
    
    st.markdown("### API Status")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Tavily API**")
    with col2:
        if tavily_key:
            st.markdown("✅ Connected")
        else:
            st.markdown("❌ Missing")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Groq API**")
    with col2:
        if groq_key:
            st.markdown("✅ Connected")
        else:
            st.markdown("❌ Missing")
    
    if not (tavily_key and groq_key):
        st.warning("Some API keys are missing. Please check your .env file.")

main_container = st.container()

with main_container:
    st.markdown('<h1 style="text-align: center; color: white; ;">Research any topic you want</h1>', unsafe_allow_html=True)
    st.markdown('<div class="chat-container" id="chat-container">', unsafe_allow_html=True)
    
    # Display conversation history
    for i, message in enumerate(st.session_state.messages):
        if message["role"] == "user":
            st.markdown(f"""
            <div class="chat-message">
                <div class="user-message">{message["content"]}</div>
                <div class="user-icon">👤</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            # Check if there's thinking content
            thinking = message.get("thinking", None)
            content = format_markdown_safely(message["content"])
            
            st.markdown(f"""
            <div class="chat-message">
                <div class="agent-icon">🤖</div>
                <div class="agent-message">
                    <div class="markdown-content">{content}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            if thinking:
                st.markdown(f"""
                <div class="thinking-text">
                    <strong>Thinking process:</strong><br>{thinking}
                </div>
                """, unsafe_allow_html=True)
            
            # Display used tools if available
            used_tools = message.get("used_tools", [])
            if used_tools:
                tool_emojis = {
                    'arxiv': '📑',
                    'wikipedia': '🌐',
                    'tavily_search_results_json': '🔎'
                }
                tool_names = {
                    'arxiv': 'ArXiv',
                    'wikipedia': 'Wikipedia',
                    'tavily_search_results_json': 'Web Search'
                }
                tools_text = "    ".join([f"{tool_emojis.get(tool, '')} {tool_names.get(tool, tool)}" for tool in used_tools])
                st.markdown(f"""
                <div style="background-color: rgba(54, 69, 79, 0.45);" class="thinking-text">
                    <strong>Tools used:</strong><br>{tools_text}
                </div>
                """, unsafe_allow_html=True)
    
    if 'message_container' not in st.session_state:
        st.session_state.message_container = st.empty()
    
    if st.session_state.thinking:
        st.markdown(f"""
        <div class="chat-message">
            <div class="agent-icon loading-icon">🤖</div>
            <div class="agent-message">
                <div class="markdown-content">{get_thinking_message(st.session_state.messages[-1].get('used_tools', []))}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)


st.markdown('<div class="input-area">', unsafe_allow_html=True)
col1, col2 = st.columns([6, 1])
with col1:
    user_input = st.text_input("Ask me anything...", key="user_input", label_visibility="collapsed", value=st.session_state.input_value)
with col2:
    submit_button = st.button("Send", use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)


if submit_button and user_input:
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })
    
    st.session_state.input_value = ""
    
    with main_container:
        st.session_state.thinking = True
        st.rerun()


if st.session_state.thinking:
    last_user_message = None
    for msg in reversed(st.session_state.messages):
        if msg["role"] == "user":
            last_user_message = msg["content"]
            break
    
    if last_user_message:
        response = process_query(last_user_message)
        
        tools_used = st.session_state.messages[-1].get('used_tools', []) if st.session_state.messages else []
        
        stream_response(response)
        
        st.rerun()

if __name__ == "__main__":
    # Nothing to do here as Streamlit handles the application flow
    pass