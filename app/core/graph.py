import streamlit as st
from core.state import AppState
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from agents.data_collection import data_collection_node
from agents.analysis import analysis_node

# ── Graph ──────────────────────────────────────────────────────────────────────
@st.cache_resource
def get_graph():
    builder = StateGraph(AppState)
    builder.add_node("data_collection", data_collection_node)
    builder.add_node("analysis", analysis_node)
    builder.add_edge(START, "data_collection")
    builder.add_edge("data_collection", "analysis")
    builder.add_edge("analysis", END)

    memory = MemorySaver()
    return builder.compile(checkpointer=memory)
