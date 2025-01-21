from langgraph.types import Send
from langchain_core.messages import HumanMessage, AIMessage
import json
from prompts import OUTLINE_PROMPT, PARAGRAPH_PROMPT, INSIGHTS_PROMPT, TRANSCRIPT_PROMPT, FACT_CHECKER_PROMPT, generate_final_article
from utils import remove_json_markers
from state import State, ParagraphState


def select_next(state: State):
    current_index = state["current_index"]

    if current_index >= len(state["outline"]["children"]):
        return "final_review"

    state["current_index"] = current_index + 1

    return "next_paragraph"

def outline_writer(state: State, model):
    # Get the messages from the state
    print("writing outline")
    print("------------------")

    prompt = HumanMessage(content=OUTLINE_PROMPT(
        original_article={state['original_article']}
    ))
    response = model.invoke(prompt)
    
    formatted_response = remove_json_markers(response.content)
    formatted_response = json.loads(formatted_response)

    return {
        "outline": formatted_response,
        "messages": [AIMessage(content=response.content)]
    }
    
def paragraph_writer(state: ParagraphState, model):
    node = state['node']
    print("writing paragraph:", node["node_id"])

    new_message = HumanMessage(content=PARAGRAPH_PROMPT.format(
        original_article=state['original_article'],
        node=node
    ))


    response = model.invoke([new_message])

    new_node = {
        "node_id": node['node_id'],
        "title": node['title'],
        "full_text": response.content
    }

    return {
        "paragraphs": [new_node],
        "messages": [AIMessage(content=response.content)]
    }

def continue_to_paragraphs(state: State) -> list[Send]:
    """Generate Send objects for each subject to be processed in parallel."""
    return [Send("paragraph_node", {"original_article": state["original_article"], "node": s}) for s in state["outline"]["children"]]

def final_writer(state: State):
    print("FINAL --------------")
    print("  ", state["outline"]["title"])
    for item in state['paragraphs']:
        print("    ", item['node_id'])
    
    outline = state["outline"]
    paragraphs = state["paragraphs"]
    # Create a lookup table from the current order in `state['outline']['children']`
    order = {item['node_id']: index for index, item in enumerate(state['outline']['children'])}

    # Sort `state['paragraphs']` based on the lookup table
    paragraphs.sort(key=lambda x: order.get(x['node_id'], float('inf')))
    
    return {
        "final_article": generate_final_article(
            title=outline['title'],
            insights=state['insights'],
            outline=paragraphs,
            transcript=state['transcript'],
        )
    }

def insights_writer(state: State, model):
    print("writing top insights")
    print("------------------")
    new_message = HumanMessage(content=INSIGHTS_PROMPT.format(
        original_article=state['original_article']
    ))
    response = model.invoke([new_message])
    return {
        "insights": response.content,
        "messages": [AIMessage(content=response.content)]
    }

def transcript_writer(state: State, model):
    new_message = HumanMessage(content=TRANSCRIPT_PROMPT.format(
        original_article=state['original_article'],
        outline=state['outline']
    ))

    response = model.invoke([new_message])

    return {
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
