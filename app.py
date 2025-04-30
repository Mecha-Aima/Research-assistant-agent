import streamlit as st
import time
import uuid
import os
from typing import Any
import random

from graph import run_query_with_history
from utils import extract_thinking, format_markdown_safely, prepare_messages_for_display
from langchain_core.messages import HumanMessage, AIMessage


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
        color: rgba(70, 70, 70, 0.85);
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
        color: white;
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
        background-color: ;
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
        background-color: white;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 5px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        transition: transform 0.2s, box-shadow 0.2s;
        color: black;
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


def stream_response(response):
    """
    Simulate streaming effect for the agent's response.
    
    Args:
        response: The response to stream
    """
    placeholder = st.empty()
    thinking, cleaned_response = extract_thinking(response)
    print(response)
    
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
        
        # Adjust the delay to control streaming speed
        time.sleep(random.uniform(0.01, 0.03))
    
    # Final display without cursor
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
    # Set thinking state to true
    st.session_state.thinking = True
    
    # Add user message to history
    st.session_state.messages.append({
        "role": "user",
        "content": user_query
    })
    
    # Call the agent
    try:
        response = run_query_with_history(st.session_state.messages, st.session_state.thread_id)
        
        if response and 'messages' in response and response['messages']:
            # Get the last message from the agent
            agent_message = response['messages'][-1]
            agent_response = agent_message.content
            
            # Process the response to extract thinking
            thinking, cleaned_response = extract_thinking(agent_response)
            
            # Add agent message to history
            st.session_state.messages.append({
                "role": "assistant",
                "content": agent_response,
                "thinking": thinking
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
        # Set thinking state to false
        st.session_state.thinking = False


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
    
    # Settings
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
    st.markdown('<h1>Research any topic you want!</h1>', unsafe_allow_html=True)
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
            
            # Display thinking if available
            if thinking:
                st.markdown(f"""
                <div class="thinking-text">
                    <strong>Thinking process:</strong><br>{thinking}
                </div>
                """, unsafe_allow_html=True)
    
    if 'message_container' not in st.session_state:
        st.session_state.message_container = st.empty()
    
    if st.session_state.thinking:
        st.markdown("""
        <div class="chat-message">
            <div class="agent-icon loading-icon">🤖</div>
            <div class="agent-message">
                <div class="markdown-content">Thinking...</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)


st.markdown('<div class="input-area">', unsafe_allow_html=True)
col1, col2 = st.columns([6, 1])
with col1:
    user_input = st.text_input("Ask me anything...", key="user_input", label_visibility="collapsed")
with col2:
    submit_button = st.button("Send", use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)


if submit_button and user_input:
    # First add user's message to session state
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })
    
    # Then process and display the response
    with main_container:
        # Set thinking state
        st.session_state.thinking = True
        
        # Force a rerun to show the user's message and thinking state
        st.rerun()


if st.session_state.thinking:
    # Get the last user message
    last_user_message = None
    for msg in reversed(st.session_state.messages):
        if msg["role"] == "user":
            last_user_message = msg["content"]
            break
    
    if last_user_message:
        # Process the query
        response = process_query(last_user_message)
        
        # Stream the response
        stream_response(response)
        
        # Force a rerun to update the UI
        st.rerun()

if __name__ == "__main__":
    # Nothing to do here as Streamlit handles the application flow
    pass