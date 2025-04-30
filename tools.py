from langchain_community.tools import ArxivQueryRun, WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper, ArxivAPIWrapper
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.messages import HumanMessage
from langchain_groq import ChatGroq
from dotenv import load_dotenv
load_dotenv()

import os 

os.environ["TAVILY_API_KEY"]=os.getenv("TAVILY_API_KEY")
os.environ["GROQ_API_KEY"]=os.getenv("GROQ_API_KEY")

api_wrapper_arxiv=ArxivAPIWrapper(top_k_results=2, doc_content_chars_max=500)
arxiv=ArxivQueryRun(api_wrapper=api_wrapper_arxiv, description="Query arxiv papers")

api_wrapper_wiki=WikipediaAPIWrapper(top_k_results=2, doc_content_chars_max=500)
wiki=WikipediaQueryRun(api_wrapper=api_wrapper_wiki, description="Query wikipedia articles")


tavily = TavilySearchResults()

tools=[arxiv, wiki, tavily]
llm = ChatGroq(model="qwen-qwq-32b")

llm_with_tools =llm.bind_tools(tools=tools)

if __name__ == "__main__":
    response = (llm_with_tools.invoke([HumanMessage(content="Latest developments in Quantum Computing. Also mention some valid research papers on the topic")]))
    print(response.tool_calls)