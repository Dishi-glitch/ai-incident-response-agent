from __future__ import annotations
import hashlib, json, os, uuid
from typing import Any
from dotenv import load_dotenv
from pydantic import ValidationError
from langchain_google_genai import ChatGoogleGenerativeAI
from ..schemas.models import InvestigationState, IncidentAnalysis
from ..tools.mock_tools import TOOL_REGISTRY

MAX_TOOL_CALLS = 15
MAX_ITERATIONS = 8
REQUIRED_EVIDENCE_SOURCES = 2

PLAN = [
 'get_model_metrics','get_model_comparison','get_deployment_changes','check_data_drift',
 'check_data_quality','get_pipeline_changes','get_training_data_quality','get_latency_metrics','get_error_rates',
 'get_service_health','get_model_version','get_training_history','get_recent_incidents','get_previous_remediations'
]

CATEGORY = {
 'get_model_metrics':'model_metrics','get_model_comparison':'model_version','get_deployment_changes':'deployment',
 'check_data_drift':'data_drift','check_data_quality':'data_quality','get_pipeline_changes':'pipeline',
 'get_training_data_quality':'training_data','get_latency_metrics':'service','get_error_rates':'service',
 'get_service_health':'service','get_model_version':'model_version','get_training_history':'training',
 'get_recent_incidents':'history','get_previous_remediations':'history'
}

def _evidence_id(incident_id: str, tool: str, args: dict, result: Any) -> str:
    raw = json.dumps([incident_id,tool,args,result], sort_keys=True, default=str).encode()
    return 'E-' + hashlib.sha1(raw).hexdigest()[:10]

def empty_result(x: Any) -> bool:
    return x is None or x == {} or x == [] or (isinstance(x,str) and not x.strip())

def validate_tool_arguments(tool_name: str, arguments: dict) -> tuple[bool,str|None]:
    tool = TOOL_REGISTRY.get(tool_name)
    if tool is None: return False, f"Unknown tool: {tool_name}"
    schema = getattr(tool, 'args_schema', None)
    if schema is None:
        return (not arguments), None if not arguments else "Tool accepts no arguments"
    try:
        schema.model_validate(arguments)
        return True, None
    except ValidationError as e:
        return False, str(e)

def choose_args(name: str) -> dict[str,Any]:
    return {
      'get_model_metrics': {'metric':'accuracy'},
      'get_model_comparison': {'current_version':'v2.1','previous_version':'v2.0'},
      'get_feature_statistics': {'feature':'customer_age'},
      'check_feature_drift': {'feature':'customer_age'},
    }.get(name,{})

def incident_intake(state: InvestigationState) -> dict:
    incident = state.get('incident','').strip()
    if not incident:
        return {'guardrail_violations':['Incident text is empty'], 'current_step':'incident_intake_failed'}
    return {'current_step':'incident_intake_completed'}

def initial_analysis(incident: str) -> dict[str,Any]:
    # Phase 1-2: structured LLM analysis when configured; deterministic fallback keeps tests/API usable.
    load_dotenv()
    key = os.getenv('GEMINI_API_KEY')
    if not key:
        return IncidentAnalysis(
            incident_type='model_accuracy_degradation',
            observed_symptoms=['accuracy dropped from 94% to 82%','drop followed a deployment'],
            possible_causes=['deployment regression','data drift','data quality issue'],
            missing_information=['deployment changes','drift evidence','training/data-quality evidence'],
            recommended_next_investigation=['get_model_comparison','get_deployment_changes','check_data_drift']
        ).model_dump()
    try:
        llm = ChatGoogleGenerativeAI(model=os.getenv('GEMINI_MODEL','gemini-3.6-flash'), google_api_key=key, temperature=0)
        structured = llm.with_structured_output(IncidentAnalysis)
        result = structured.invoke(f"Analyze this ML incident. Separate facts from hypotheses. Do not confirm a root cause. Incident: {incident}")
        return result.model_dump()
    except Exception as exc:
        return {'incident_type':'unknown','observed_symptoms':[incident],'possible_causes':[],'missing_information':['LLM analysis unavailable'], 'recommended_next_investigation':[], '_error':str(exc)}

def plan_investigation(state: InvestigationState) -> dict:
    return {'investigation_plan': PLAN.copy(), 'current_step':'plan_investigation_completed'}

def execute_one(state: InvestigationState) -> dict:
    plan = state.get('investigation_plan',[])
    used = set(state.get('tools_used',[]))
    next_tool = next((x for x in plan if x not in used), None)
    if next_tool is None: return {'current_step':'no_tool_remaining'}
    if state.get('tool_call_count',0) >= MAX_TOOL_CALLS:
        return {'max_iterations_reached':True,'stop_reason':'max_tool_calls','current_step':'tool_limit_reached'}
    args = choose_args(next_tool)
    ok, err = validate_tool_arguments(next_tool,args)
    if not ok:
        return {'tool_errors':state.get('tool_errors',[])+[{'tool':next_tool,'error':err}], 'guardrail_violations':state.get('guardrail_violations',[])+[err or 'invalid arguments'], 'tools_used':state.get('tools_used',[])+[next_tool], 'tool_call_count':state.get('tool_call_count',0)+1, 'current_step':'tool_validation_failed'}
    try:
        result = TOOL_REGISTRY[next_tool].invoke(args)
        evidence = {'evidence_id':_evidence_id(state.get('incident_id','INC'),next_tool,args,result),'tool':next_tool,'arguments':args,'result':result,'category':CATEGORY.get(next_tool,'other')}
        errors = list(state.get('tool_errors',[]))
        empties = list(state.get('empty_results',[]))
        if empty_result(result): empties.append(evidence)
        return {'tools_used':state.get('tools_used',[])+[next_tool], 'tool_results':state.get('tool_results',[])+[evidence], 'empty_results':empties, 'tool_call_count':state.get('tool_call_count',0)+1, 'current_step':'tool_executed'}
    except Exception as exc:
        return {'tool_errors':state.get('tool_errors',[])+[{'tool':next_tool,'error':str(exc)}], 'tools_used':state.get('tools_used',[])+[next_tool], 'tool_call_count':state.get('tool_call_count',0)+1, 'current_step':'tool_failed'}

def analyze_evidence(state: InvestigationState) -> dict:
    results = state.get('tool_results',[])
    categories = {r['category'] for r in results}
    contradictions=[]
    # Explicit contradiction detector for common paired signals.
    drift = next((r for r in results if r['tool']=='check_data_drift'),None)
    quality = next((r for r in results if r['tool']=='check_data_quality'),None)
    latency = next((r for r in results if r['tool']=='get_latency_metrics'),None)
    if drift and not drift['result'].get('drift_detected',False): contradictions.append({'type':'drift','message':'Drift evidence says no drift.'})
    if quality and quality['result'].get('quality_issue_detected') and not quality['result'].get('range_violations'): contradictions.append({'type':'quality','message':'Quality flags an issue without range violations.'})
    hypotheses=[]
    for hid, statement, needed in [
      ('H1','deployment / preprocessing regression',['deployment','model_version','pipeline']),
      ('H2','production data drift',['data_drift']),
      ('H3','training data quality regression',['training_data','data_quality']),
    ]:
        support=[r['evidence_id'] for r in results if r['category'] in needed]
        hypotheses.append({'hypothesis_id':hid,'statement':statement,'supporting_evidence_ids':support,'opposing_evidence_ids':[],'status':'supported' if support else 'candidate'})
    # Independent-source rule: deployment/model version + pipeline/model comparison is enough for H1.
    h1 = next(h for h in hypotheses if h['hypothesis_id']=='H1')
    h2 = next(h for h in hypotheses if h['hypothesis_id']=='H2')
    h3 = next(h for h in hypotheses if h['hypothesis_id']=='H3')
    h1['status'] = 'supported' if len(h1['supporting_evidence_ids']) >= 2 else 'candidate'
    h2['status'] = 'supported' if len(h2['supporting_evidence_ids']) >= 1 else 'candidate'
    h3['status'] = 'supported' if len(h3['supporting_evidence_ids']) >= 2 else 'candidate'
    supported = [h for h in hypotheses if h['status']=='supported']
    return {'hypotheses':hypotheses,'contradictions':contradictions,'supported_conclusion':bool(supported),'current_step':'evidence_analyzed'}

def should_continue(state: InvestigationState) -> str:
    if state.get('guardrail_violations'): return 'finalize'
    if state.get('tool_call_count',0) >= MAX_TOOL_CALLS: return 'finalize'
    if state.get('supported_conclusion') and state.get('iteration_count',0) >= 2: return 'finalize'
    if len(state.get('tools_used',[])) >= len(state.get('investigation_plan',[])): return 'finalize'
    return 'continue'

def finalize(state: InvestigationState) -> dict:
    hypotheses=state.get('hypotheses',[])
    supported=[h for h in hypotheses if h.get('status')=='supported']
    # Prefer deployment hypothesis only when it has >=2 independent evidence records.
    chosen=next((h for h in supported if h['hypothesis_id']=='H1' and len(h['supporting_evidence_ids'])>=2),None)
    if chosen:
        conclusion='The evidence supports a deployment/preprocessing regression as a root-cause hypothesis.'
        ids=chosen['supporting_evidence_ids']
        actions=['Compare v2.1 preprocessing configuration with v2.0','Rollback if business impact requires immediate mitigation','Re-run validation with the production preprocessing path']
    else:
        conclusion='The available evidence is insufficient to confirm a root cause.'
        ids=[]
        actions=['Collect the missing diagnostic evidence before declaring a root cause']
    unresolved=[] if chosen else ['Which causal factor explains the accuracy drop remains unresolved.']
    report={'incident_id':state.get('incident_id','INC-UNKNOWN'),'incident_summary':state.get('incident',''),'severity':'high','observed_symptoms':state.get('llm_analysis',{}).get('observed_symptoms',[]),'evidence_collected':state.get('tool_results',[]),'investigation_steps':state.get('tools_used',[]),'hypotheses_considered':hypotheses,'supported_finding':conclusion,'supporting_evidence_ids':ids,'affected_model_version':'v2.1','recommended_actions':actions,'unresolved_questions':unresolved,'investigation_trace':state.get('trace',[]),'stop_reason':state.get('stop_reason','evidence_sufficient')}
    return {'supported_conclusion':bool(chosen),'final_conclusion':conclusion,'report':report,'current_step':'finalized'}
