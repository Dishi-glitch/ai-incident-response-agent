from __future__ import annotations
from typing import Any, Literal, TypedDict
from pydantic import BaseModel, Field, field_validator

class IncidentAnalysis(BaseModel):
    incident_type: str
    observed_symptoms: list[str] = Field(default_factory=list)
    possible_causes: list[str] = Field(default_factory=list)
    missing_information: list[str] = Field(default_factory=list)
    recommended_next_investigation: list[str] = Field(default_factory=list)

class ModelMetricsInput(BaseModel):
    metric: Literal['accuracy','precision','recall','f1']

class ClassMetricsInput(BaseModel):
    class_name: str | None = None

class FeatureInput(BaseModel):
    feature: str

class ModelComparisonInput(BaseModel):
    current_version: str = 'v2.1'
    previous_version: str = 'v2.0'

class InvestigationState(TypedDict, total=False):
    incident: str
    incident_id: str
    investigation_plan: list[str]
    tools_used: list[str]
    tool_results: list[dict[str, Any]]
    tool_errors: list[dict[str, Any]]
    empty_results: list[dict[str, Any]]
    contradictions: list[dict[str, Any]]
    guardrail_violations: list[str]
    tool_call_count: int
    iteration_count: int
    max_iterations_reached: bool
    supported_conclusion: bool
    final_conclusion: str
    report: dict[str, Any]
    hypotheses: list[dict[str, Any]]
    current_step: str
    stop_reason: str
    trace: list[dict[str, Any]]
    llm_analysis: dict[str, Any]

class Evidence(BaseModel):
    evidence_id: str
    tool: str
    arguments: dict[str, Any] = Field(default_factory=dict)
    result: Any
    category: str

class Hypothesis(BaseModel):
    hypothesis_id: str
    statement: str
    supporting_evidence_ids: list[str] = Field(default_factory=list)
    opposing_evidence_ids: list[str] = Field(default_factory=list)
    status: Literal['candidate','supported','weakened','unresolved'] = 'candidate'

class IncidentReport(BaseModel):
    incident_id: str
    incident_summary: str
    severity: str
    observed_symptoms: list[str]
    evidence_collected: list[dict[str, Any]]
    investigation_steps: list[str]
    hypotheses_considered: list[dict[str, Any]]
    supported_finding: str
    supporting_evidence_ids: list[str]
    affected_model_version: str | None = None
    recommended_actions: list[str]
    unresolved_questions: list[str]
    investigation_trace: list[dict[str, Any]]
    stop_reason: str
