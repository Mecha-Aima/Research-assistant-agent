from langchain_core.messages import HumanMessage, AIMessage, AnyMessage, SystemMessage
from typing import Annotated
from langgraph.graph.message import MessagesState, add_messages
from langgraph.checkpoint.memory import MemorySaver
from IPython.display import Image, display
from langgraph.graph import StateGraph, START, END 
from langgraph.prebuilt import ToolNode, tools_condition
from tools import *

# Agentic Workflow Architecture
def build_graph() -> StateGraph:
    def merge_unique_lists(left: list[str], right: list[str]) -> list[str]:
        return list(set(left) | set(right))

    class State(MessagesState):
        messages: Annotated[list[AnyMessage], add_messages]
        tools_used: Annotated[list[str], merge_unique_lists]

    def tool_calling_llm(state: State) -> dict:
        if "messages" not in state or not state["messages"]:
            response = llm_with_tools.invoke([HumanMessage(content="Hello")])
            return {'messages': [response], 'tools_used': []}
        
        message = llm_with_tools.invoke(state["messages"])
        tools_used = list(state.get("tools_used", []))
        for tool in getattr(message, "tool_calls", []):
            if tool['name'] not in tools_used:
                tools_used.append(tool['name'])
                print(f"Tool {tool['name']} used")
        return {'messages': [message], 'tools_used': tools_used}


    builder = StateGraph(State)
    builder.add_node("tool_calling_llm", tool_calling_llm)
    builder.add_node("tools", ToolNode(tools))

    builder.add_edge(START, "tool_calling_llm")
    builder.add_conditional_edges("tool_calling_llm", tools_condition)
    builder.add_edge("tools", "tool_calling_llm")

    memory = MemorySaver()
    graph = builder.compile(checkpointer=memory)
    return graph

def run_query(query: str, thread_id: str):
    graph = build_graph()
    config = {'configurable': {'thread_id': '1'}}
    response= graph.invoke({"messages": [HumanMessage(content=query)], "tools_used": []}, config=config)
    return response

def run_query_with_history(messages, thread_id):
    graph = build_graph()
    config = {'configurable': {'thread_id': thread_id}}

    # Add system message at the beginning
    system_message = SystemMessage(content="""You are an AI research assistant with specialized knowledge in many domains. 
Your primary goal is to provide accurate and well-researched information. When you're not completely certain about something, 
always prefer to look up sources using the available tools rather than making assumptions. Use the following tools to gather information:
- ArXiv for scientific papers and research
- Wikipedia for general knowledge and background information
- Tavily for current web search results

Always cite your sources and be transparent about where your information comes from. If you're unsure about something, 
acknowledge the uncertainty and use the tools to find accurate information.""")

    langchain_messages = [system_message]  # Start with system message
    for message in messages:
        if message["role"] == "user":
            langchain_messages.append(HumanMessage(content=message["content"]))
        elif message["role"] == "assistant":
            langchain_messages.append(AIMessage(content=message["content"]))
    
    response = graph.invoke({"messages": langchain_messages, "tools_used": []}, config=config)
    
    return response

if __name__ == '__main__':
    query = input("What do you want to know? ")
    response = run_query_with_history([{"role": "user", "content": query}], 1) 
    print(response.get("tools_used", []))
    if response and 'messages' in response:
        for m in response['messages']:
            m.pretty_print()
    