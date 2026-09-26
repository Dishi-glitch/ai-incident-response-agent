# AI Incident Response Agent

An evidence-first Agentic AI system for investigating ML incidents.

> **Investigate WHY an ML system failed — do not guess.**

## Core idea

Given an incident such as:

> "Model accuracy dropped from 94% to 82% after yesterday's deployment."

the agent should not immediately declare a root cause. It should:

1. Parse the incident.
2. Create an investigation plan.
3. Select investigation tools.
4. Execute tools and collect evidence.
5. Track errors, empty results, and contradictions.
6. Reassess whether more evidence is needed.
7. Stop safely when sufficient evidence exists or a deterministic limit is reached.
8. Produce an evidence-backed conclusion and report.

## Implemented phases

- LLM + Gemini analyzer
- Pydantic structured output
- LangChain tool calling
- 28 deterministic investigation tools
- Typed tool argument validation
- Evidence collection and traceability
- Explicit LangGraph investigation state
- Conditional routing and investigation loops
- Deterministic stopping limits
- Guardrails for failures, empty results, contradictions, invalid arguments, and unsupported conclusions

## Deliberately not included yet

- RAG
- Evaluation benchmark framework
- FastAPI / production API
- Docker / deployment

The goal is to master the investigation architecture before adding these layers.

## Project structure

```text
ai-incident-response-agent/
├── data/
│   └── incidents/
│       └── demo.json
├── docs/
│   ├── ARCHITECTURE.md
│   └── PHASES.md
├── src/
│   ├── agents/
│   │   └── investigator.py
│   ├── graph/
│   │   └── workflow.py
│   ├── schemas/
│   │   └── models.py
│   └── tools/
│       └── mock_tools.py
├── tests/
│   ├── test_tools.py
│   └── test_workflow.py
├── .env.example
├── requirements.txt
└── README.md
```

## Setup

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Create `.env` from `.env.example` and add your Gemini API key.

## Run

```powershell
python -m src.agents.investigator
```

Run tests:

```powershell
pytest
```

## Design principle

The LLM is responsible for reasoning and choosing investigation actions. It is **not** trusted to invent telemetry or declare a root cause without supporting evidence.

The tools provide the evidence. The state records the investigation. The guardrails enforce safety boundaries.
