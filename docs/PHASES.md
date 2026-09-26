# AI Incident Response Agent — Current Phase Map

This repository intentionally stops before RAG, evaluation, and productionization.

## Phase 1 — LLM Analyzer
Gemini receives an incident and produces an initial structured analysis.

## Phase 2 — Structured Output
Pydantic schemas enforce predictable incident-analysis output.

## Phase 3 — Tool Calling
The agent can request investigation tools rather than relying only on model knowledge.

## Phase 4 — Investigation Toolset
The repository contains deterministic tools covering model metrics, class performance, confusion patterns, predictions, data quality/drift, model versions, deployment, service health, training/pipeline state, and historical incident signals.

## Phase 5 — Tool Validation & Evidence Collection
Tool names and arguments are validated. Results are recorded as evidence, including errors and empty results.

## Phase 6 — LangChain Tool Integration
Tools use LangChain-compatible schemas and the Gemini model can be bound to the tool registry.

## Phase 7 — LangGraph State Machine
The investigation is represented as explicit state and graph nodes:

START → incident_intake → plan_investigation → execute_tool → analyze_evidence → synthesize_report → END

## Phase 8 — Conditional Routing, Loops & Stopping
The graph can route back for additional evidence while enforcing deterministic tool-call/iteration limits.

## Phase 9 — Guardrails
The agent handles invalid tool arguments, unknown tools, tool failures, empty results, contradictory evidence, unsupported conclusions, and investigation limits.

## Intentionally Deferred
- RAG / retrieval
- Evaluation benchmark framework
- Production API / deployment / Docker

These are deliberately excluded so the core investigation architecture can be understood and stabilized first.
