from typing import TypedDict, Annotated, TypeVar
from langgraph.graph import Graph, StateGraph, START, END
from langgraph.types import Send
from langgraph.prebuilt import ToolExecutor
from operator import itemgetter
from langchain_core.messages import HumanMessage, AIMessage
import json
import operator
import os
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from prompts import OUTLINE_PROMPT, PARAGRAPH_PROMPT, WHOLE_ARTICLE_PROMPT, INSIGHTS_PROMPT, TRANSCRIPT_PROMPT, FACT_CHECKER_PROMPT

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

T = TypeVar('T')

def take_latest(old_value, new_value) -> T:
    return new_value

# Define the state schema
class State(TypedDict):
    original_article: Annotated[str, take_latest]
    outline: Annotated[dict, take_latest]
    final_response: Annotated[list[str], operator.add]
    final_article: Annotated[str, operator.concat]
    insights: Annotated[str, operator.concat]
    transcript: Annotated[str, operator.concat]
    messages: Annotated[list, operator.add]
    current_index: Annotated[int, take_latest]

def select_next(state: State):
    current_index = state["current_index"]

    if current_index >= len(state["outline"]["children"]):
        return "final_review"

    state["current_index"] = current_index + 1

    return "next_paragraph"

def remove_json_markers(text):
    # Define the markers
    start_marker = "```json"
    end_marker = "```"

    # Remove the start marker if it exists
    if text.startswith(start_marker):
        text = text[len(start_marker):]

    # Remove the end marker if it exists
    if text.endswith(end_marker):
        text = text[:-len(end_marker)]

    # Strip any extra whitespace that might remain
    return text.strip()

def start(state: State):
    print("Starting now...")
    return {
        **state
    }

# First LLM call handler
def first_call(state: State, model):
    # Get the messages from the state
    messages = state["messages"]
    

    prompt = HumanMessage(content=OUTLINE_PROMPT(
        original_article={state['original_article']}
    ))
    messages.append(prompt)
    print("writing outline")
    # Make the first LLM call
    print("------------------\n")
    print(prompt)
    response = model.invoke(messages)
    formatted_response = remove_json_markers(response.content)

    formatted_response = json.loads(formatted_response)

    # Update the state with the response
    return {
        **state,
        "outline": formatted_response,
        "messages": [AIMessage(content=response.content)]
    }

# Second LLM call handler
def second_call(state: State, model):
    current_index = state["current_index"]
    node = state['outline']['children'][current_index]
    print("writing node", node["node_id"], "out of", len(state['outline']['children']))

    # Create a prompt that includes the result from the first call
    new_message = HumanMessage(content=PARAGRAPH_PROMPT.format(
        original_article=state['original_article'],
        node=node
    ))
    print("------------------\n")
    print(new_message)

    # Make the second LLM call
    response = model.invoke([new_message])
    state['outline']['children'][current_index]['full_text'] = response.content
    # Update the state with the final response
    return {
        **state,
        "current_index": current_index + 1,
        "final_response": state["final_response"] + [f"{node['node_id']} {response.content}"],
        "messages": [AIMessage(content=response.content)]
    }

def final_review(state: State, model):
    print("putting everything together ...")
    outline = state["outline"]
    if "content" in outline:
        del outline["content"]
    for item in outline["children"]:
        if "content" in item:
            del item["content"]
    print(outline)

    new_message = HumanMessage(content=WHOLE_ARTICLE_PROMPT.format(
        insights=state['insights'],
        outline=outline
    ))
    response = model.invoke([new_message])

    return {
        **state,
        "final_article": response.content,
        "messages": [AIMessage(content=response.content)]
    }

def top_insights(state: State, model):
    print("top insights")
    new_message = HumanMessage(content=INSIGHTS_PROMPT.format(
        original_article=state['original_article']
    ))
    print("------------------\n")
    print(new_message)
    response = model.invoke([new_message])
    return {
        **state,
        "insights": response.content,
        "messages": [AIMessage(content=response.content)]
    }

def transcript(state: State, model):
    new_message = HumanMessage(content=TRANSCRIPT_PROMPT.format(
        original_article=state['original_article'],
        outline=state['outline']
    ))

    response = model.invoke([new_message])
    state['final_article'] += f"""
        ---
        ## 详细对话
        {response.content}
        """
    return {
        **state,
        "transcript": response.content,
        "messages": [AIMessage(content=response.content)]
    }

def fact_checker(state: State, model):
    new_message = HumanMessage(content=FACT_CHECKER_PROMPT.format(
        original_article=state['original_article'],
        final_article=state['final_article']
    ))

    response = model.invoke([new_message])
    print("Score:", response.content)
    return {
        "messages": [AIMessage(content=response.content)]
    }

def create_sequential_graph(llm1, llm2):
    # Create a new graph
    workflow = StateGraph(State)

    # Add the first LLM call node
    workflow.add_node("start", lambda state: start(state))
    workflow.add_node("write_outline", lambda state: first_call(state, llm2))

    # Add the second LLM call node
    workflow.add_node("next_paragraph", lambda state: second_call(state, llm2))

    workflow.add_node("top_insights", lambda state: top_insights(state, llm2))
    workflow.add_node("write_transcript", lambda state: transcript(state, llm2))
    workflow.add_node("final_review", lambda state: final_review(state, llm2))
    workflow.add_node("fact_checker", lambda state: fact_checker(state, llm1))

    # Create the sequential flow
    workflow.add_edge(START, "start")
    workflow.add_edge("start", "write_outline")
    workflow.add_edge("start", "top_insights")
    workflow.add_conditional_edges("write_outline", lambda state: select_next(state))
    workflow.add_conditional_edges("next_paragraph", lambda state: select_next(state))
    workflow.add_edge(["top_insights", "final_review"], "write_transcript")
    workflow.add_edge("write_transcript", "fact_checker")
    workflow.add_edge("fact_checker", END)

    # Compile the graph
    app = workflow.compile()

    return app

# Example usage
def run_workflow(input_message):
    # Create the graph
    app = create_sequential_graph(llm1, llm2)

    # Initialize the state
    initial_state = {
        "original_article": input_message,
        "messages": [],
        "outline": {},
        "final_response": [],
        "current_index": 0,
        "final_article": "",
        "transcript": "",
        "insights": ""
    }

    # Run the workflow
    result = app.invoke(initial_state)

    return result

graph = create_sequential_graph(llm1, llm2)