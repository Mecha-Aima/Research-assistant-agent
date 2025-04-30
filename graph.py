from langchain_core.messages import HumanMessage, AIMessage
from typing import Annotated
from langgraph.graph.message import MessagesState
from langgraph.checkpoint.memory import MemorySaver
from IPython.display import Image, display
from langgraph.graph import StateGraph, START, END 
from langgraph.prebuilt import ToolNode, tools_condition
from tools import *

# Agentic Workflow Architecture
def build_graph() -> StateGraph:
    class State(MessagesState):
        messages = list[str]

    def tool_calling_llm(state: State) -> State:
        if "messages" not in state or not state["messages"]:
            print("No messages found in state, using default")
            return {'messages': [llm_with_tools.invoke([HumanMessage(content="Hello")])]}
        
        try:
            message = llm_with_tools.invoke(state["messages"])
            return {'messages': [message]}
        except Exception as e:
            error_message = AIMessage(content=f"<think>Error occurred during processing: {str(e)}</think>I encountered an error while processing your request. Please try again with a different query.")
            return {'messages': [error_message]}


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
    response= graph.invoke({"messages": [HumanMessage(content=query)]}, config=config)
    return response

def run_query_with_history(messages, thread_id):
    graph = build_graph()
    config = {'configurable': {'thread_id': thread_id}}

    langchain_messages = []
    for message in messages:
        if message["role"] == "user":
            langchain_messages.append(HumanMessage(content=message["content"]))
        elif message["role"] == "assistant":
            langchain_messages.append(AIMessage(content=message["content"]))
    
    response = graph.invoke({"messages": langchain_messages}, config=config)
    
    return response

if __name__ == '__main__':
    query = input("What do you want to know? ")
    response = run_query(query, 1) 
    if response and 'messages' in response:
        for m in response['messages']:
            m.pretty_print()
    