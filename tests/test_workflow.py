from src.graph.workflow import run_investigation

def test_workflow_produces_report():
    s=run_investigation("Our ML model's accuracy dropped from 94% to 82% after yesterday's deployment.",'TEST-001')
    assert s['report']['incident_id']=='TEST-001'
    assert s['tool_call_count'] <= 15
    assert s['report']['supporting_evidence_ids']

def test_evidence_ids_are_traceable():
    s=run_investigation('accuracy regression after deployment','TEST-002')
    ids={x['evidence_id'] for x in s['tool_results']}
    assert set(s['report']['supporting_evidence_ids']).issubset(ids)

def test_state_has_guardrail_fields():
    s=run_investigation('accuracy regression','TEST-003')
    for key in ['tool_errors','empty_results','contradictions','guardrail_violations','hypotheses','trace']:
        assert key in s
