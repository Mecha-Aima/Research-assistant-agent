import re
from typing import Tuple, Optional, List, Dict, Any
import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage
import markdown

def extract_thinking(text: str) -> Tuple[Optional[str], str]:
    """
    Extract content within <think> tags and return both the thinking part
    and the cleaned response without the thinking tags.
    
    Args:
        text: The text to extract thinking from
        
    Returns:
        Tuple containing (thinking_content, cleaned_text)
    """
    pattern = r'<think>(.*?)</think>'
    matches = re.findall(pattern, text, re.DOTALL)
    
    if matches:
        thinking_content = matches[0].strip()
        cleaned_text = re.sub(pattern, '', text, flags=re.DOTALL).strip()
        
        return thinking_content, cleaned_text
    
    
    return None, text

def format_markdown_safely(markdown_text: str) -> str:
    """
    Safely format markdown text to HTML, handling potential errors.
    
    Args:
        markdown_text: The markdown text to format
        
    Returns:
        HTML formatted text
    """
    try:
        
        html = markdown.markdown(
            markdown_text,
            extensions=['extra', 'codehilite', 'tables']
        )
        return html
    except Exception as e:
        st.error(f"Error formatting markdown: {e}")
        
        return markdown_text

def get_agent_icon_html(is_thinking: bool = False) -> str:
    """
    Generate HTML for the agent icon, optionally with a loading spinner.
    
    Args:
        is_thinking: Whether to show the thinking spinner
        
    Returns:
        HTML string for the agent icon
    """
    if is_thinking:
        return """
        <div style="display: flex; align-items: center; margin-bottom: 10px;">
            <div style="font-size: 1.5rem; margin-right: 10px;">🤖</div>
            <div class="loading-spinner"></div>
        </div>
        """
    else:
        return """
        <div style="display: flex; align-items: center; margin-bottom: 10px;">
            <div style="font-size: 1.5rem; margin-right: 10px;">🤖</div>
        </div>
        """