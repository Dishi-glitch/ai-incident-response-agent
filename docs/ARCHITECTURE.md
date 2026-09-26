# Architecture notes

## State
`InvestigationState` is the shared memory of the graph. It stores the incident, plan, tool results, errors, empty results, contradictions, guardrail violations, call counts, hypotheses, conclusion and trace.

## Evidence
Tool outputs are wrapped as evidence records. The evidence ID is deterministic for the same incident/tool/arguments/result.

## Stopping
The LLM does not have unilateral authority to declare an investigation complete. The graph checks evidence support and hard limits (`MAX_TOOL_CALLS=15`, `MAX_ITERATIONS=8`).

## Hypotheses
The current baseline tracks deployment/preprocessing regression, production data drift, and training/data-quality regression. The implementation is intentionally transparent so more hypothesis generators can be added later.

## Failure behavior
Unknown tools, invalid arguments, tool exceptions, empty results and contradictions are stored explicitly. Unsupported conclusions are avoided when the evidence contract is not satisfied.
