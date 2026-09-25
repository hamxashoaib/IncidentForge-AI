from langgraph.graph import StateGraph, END
from backend.agents.state import IncidentState
from backend.agents.investigator import investigate_incident
from backend.agents.rca_planner import plan_rca_and_fix

def build_incident_graph():
    workflow = StateGraph(IncidentState)

    workflow.add_node("investigator", investigate_incident)
    workflow.add_node("rca_planner", plan_rca_and_fix)

    workflow.set_entry_point("investigator")
    workflow.add_edge("investigator", "rca_planner")
    workflow.add_edge("rca_planner", END)

    return workflow.compile()

incident_pipeline = build_incident_graph()
