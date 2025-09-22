import os
from dotenv import load_dotenv
from typing import TypedDict, Annotated, List
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, ToolMessage, HumanMessage
from langgraph.prebuilt import ToolNode
from langgraph.graph import StateGraph, END

# All tools imported from the updated tools.py file
from .tools import (
    list_students,
    get_student,
    add_student,
    update_student,
    delete_student,
    get_total_students,
    get_students_by_department,
    get_recent_onboarded_students,
    get_active_students_last_7_days,
    get_cafeteria_timings,
    get_library_hours,
    get_event_schedule,
    send_email
)

# Load environment variables from .env file
load_dotenv()

# 1. Define the Agent's State
class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], lambda x, y: x + y]

# 2. Set up the Tools
tools = [
    list_students,
    get_student,
    add_student,
    update_student,
    delete_student,
    get_total_students,
    get_students_by_department,
    get_recent_onboarded_students,
    get_active_students_last_7_days,
    get_cafeteria_timings,
    get_library_hours,
    get_event_schedule,
    send_email
]
tool_executor = ToolNode(tools)

# 3. Set up the Model
# Make sure your OPENAI_API_KEY is set in your .env file
model = ChatOpenAI(model="gpt-4o", temperature=0, streaming=True)
model_with_tools = model.bind_tools(tools)

# 4. Define the Nodes of the Graph
def call_model(state: AgentState):
    """Invokes the LLM to get a response."""
    messages = state['messages']
    response = model_with_tools.invoke(messages)
    return {"messages": [response]}

def call_tool(state: AgentState):
    """Executes a tool call and returns the output."""
    last_message = state['messages'][-1]
    action = last_message.tool_calls[0]
    tool_output = tool_executor.invoke(action)
    return {"messages": [ToolMessage(content=str(tool_output), tool_call_id=action['id'])]}

# 5. Define the Edges of the Graph
def should_continue(state: AgentState):
    """Determines the next step: call a tool or end the conversation."""
    last_message = state['messages'][-1]
    if last_message.tool_calls:
        return "continue"
    return "end"

# 6. Build the Graph
workflow = StateGraph(AgentState)
workflow.add_node("agent", call_model)
workflow.add_node("action", call_tool)
workflow.set_entry_point("agent")
workflow.add_conditional_edges(
    "agent",
    should_continue,
    {"continue": "action", "end": END}
)
workflow.add_edge("action", "agent")

# This is the object that main.py will import
app = workflow.compile()
