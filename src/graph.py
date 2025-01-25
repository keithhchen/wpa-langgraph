import os
from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from .state import State
from .nodes import (
    outline_writer,
    paragraph_writer,
    final_writer,
    insights_writer,
    transcript_writer,
    select_next,
    continue_to_paragraphs,
    web_search_writer,
    summarize_writer,
    content_review_writer,
    preface_writer
)

# Load environment variables from .env file
load_dotenv()

# openai
llm1 = ChatOpenAI(model="gpt-4o-mini")
# openai_llm = openai_llm.bind(response_format={"type": "json_object"})

# deepseek
llm2 = ChatOpenAI(
    model="deepseek-chat",
    base_url="https://api.deepseek.com/v1",
    api_key=os.environ.get("DEEPSEEK_API_KEY")
    )
# deepseek_llm = deepseek_llm.bind(response_format={"type": "json_object"})

def create_sequential_graph(llm1, llm2):
    # Create a new graph
    workflow = StateGraph(State)

    # Nodes
    workflow.add_node("outline_node", lambda state: outline_writer(state, llm2))
    workflow.add_node("paragraph_node", lambda state: paragraph_writer(state, llm2))
    workflow.add_node("insights_node", lambda state: insights_writer(state, llm2))
    workflow.add_node("transcript_node", lambda state: transcript_writer(state, llm2))
    workflow.add_node("end_node", lambda state: final_writer(state))
    workflow.add_node("content_review_node", lambda state: content_review_writer(state, llm2))
    workflow.add_node("preface_node", lambda state: preface_writer(state, llm2))
    # workflow.add_node("web_search_node", lambda state: web_search_writer(state))
    # workflow.add_node("fact_checker", lambda state: fact_checker(state, llm1))
    # workflow.add_node("summarize_node", lambda state: summarize_writer(state, llm2))
    
    # Create the sequential flow
    workflow.add_edge(START, "outline_node")
    # All parallel
    workflow.add_edge("outline_node", "preface_node")
    workflow.add_conditional_edges("outline_node", continue_to_paragraphs, ["paragraph_node"])
    workflow.add_edge("outline_node", "transcript_node")
    workflow.add_edge("outline_node", "insights_node")
    # End
    workflow.add_edge(["preface_node", "paragraph_node", "transcript_node", "insights_node"], "end_node")
    workflow.add_edge("end_node", "content_review_node")
    workflow.add_edge("content_review_node", END)

    # Compile the graph
    app = workflow.compile()

    return app

# Example usage
def run_workflow(input_message, metadata=None):
    # Create the graph
    app = create_sequential_graph(llm1, llm2)

    # Initialize the state
    initial_state = {
        "original_article": input_message,
        "final_article": "",
        "messages": [],
        "outline": {},
        "transcript": "",
        "insights": "",
        "paragraphs": [],
        "metadata": metadata,
        "preface": ""
    }

    # Run the workflow
    result = app.invoke(initial_state)

    return result

graph = create_sequential_graph(llm1, llm2)