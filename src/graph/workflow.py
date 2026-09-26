from __future__ import annotations
from uuid import uuid4
from langgraph.graph import StateGraph, START, END
from ..schemas.models import InvestigationState
from ..agents.investigator import incident_intake, initial_analysis, plan_investigation, execute_one, analyze_evidence, should_continue, finalize, MAX_ITERATIONS

def llm_analysis_node(state: InvestigationState):
    return {'llm_analysis': initial_analysis(state.get('incident','')), 'current_step':'llm_analysis_completed'}

def execute_with_trace(state: InvestigationState):
    result = execute_one(state)
    event={'step':'execute_tool','tool':(result.get('tools_used') or ['unknown'])[-1], 'tool_call_count':result.get('tool_call_count',state.get('tool_call_count',0))}
    return {**result,'trace':state.get('trace',[])+[event]}

def analyze_with_iteration(state: InvestigationState):
    result=analyze_evidence(state)
    return {**result,'iteration_count':state.get('iteration_count',0)+1,'trace':state.get('trace',[])+[{'step':'analyze_evidence','iteration':state.get('iteration_count',0)+1}]}

def route(state: InvestigationState):
    if state.get('iteration_count',0) >= MAX_ITERATIONS:
        return 'finalize'
    return should_continue(state)

def build_graph():
    g=StateGraph(InvestigationState)
    g.add_node('incident_intake',incident_intake)
    g.add_node('llm_analysis',llm_analysis_node)
    g.add_node('plan_investigation',plan_investigation)
    g.add_node('execute_tool',execute_with_trace)
    g.add_node('analyze_evidence',analyze_with_iteration)
    g.add_node('finalize',finalize)
    g.add_edge(START,'incident_intake')
    g.add_edge('incident_intake','llm_analysis')
    g.add_edge('llm_analysis','plan_investigation')
    g.add_edge('plan_investigation','execute_tool')
    g.add_edge('execute_tool','analyze_evidence')
    g.add_conditional_edges('analyze_evidence',route,{'continue':'execute_tool','finalize':'finalize'})
    g.add_edge('finalize',END)
    return g.compile()

def run_investigation(incident: str, incident_id: str|None=None):
    app=build_graph()
    state: InvestigationState={
      'incident':incident,'incident_id':incident_id or f'INC-{uuid4().hex[:8].upper()}',
      'investigation_plan':[],'tools_used':[],'tool_results':[],'tool_errors':[],'empty_results':[],
      'contradictions':[],'guardrail_violations':[],'tool_call_count':0,'iteration_count':0,
      'max_iterations_reached':False,'supported_conclusion':False,'final_conclusion':'','report':{},
      'hypotheses':[],'current_step':'start','stop_reason':'','trace':[],'llm_analysis':{}
    }
    return app.invoke(state)
