from langgraph.graph import StateGraph

from agents.researcher import researcher
from agents.editor import editor
from agents.writer_agent import writer

from state.workflow_state import WorkflowState


builder = StateGraph(WorkflowState)

builder.add_node("researcher", researcher)
builder.add_node("editor", editor)
builder.add_node("writer", writer)

builder.set_entry_point("researcher")

builder.add_edge("researcher", "editor")
builder.add_edge("editor", "writer")

graph = builder.compile()