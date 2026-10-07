# llm-eval-kit

[![Python Version](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Type Checked](https://img.shields.io/badge/types-py.typed-informational)](src/llm_eval_kit/py.typed)

A modular, extensible toolkit for evaluating, benchmarking, and guarding Large Language Model (LLM) applications and RAG systems across local development and CI/CD pipelines.

---

## Overview

**`llm-eval-kit`** provides a standardized suite of utilities to evaluate LLM responses, assess retrieval quality in RAG pipelines, run LLM-as-a-Judge rubrics, enforce runtime guardrails, and export automated CI/CD quality gates.

### Key Highlights

- **Dataset Management (`golden.py`)**: Load, validate, curate, and version golden datasets and synthetic evaluation benchmarks.
- **Quantitative & Semantic Metrics (`metrics.py`)**: Built-in deterministic and semantic evaluation metrics (Exact Match, Levenshtein, ROUGE, BLEU, semantic cosine similarity, latency, and cost tracking).
- **LLM-as-a-Judge (`judge.py`)**: Automated scoring, rubric-based grading, pairwise preference comparisons, and structured reasoning extraction with custom judge LLMs.
- **RAG & Retrieval Evaluation (`retrieval_eval.py`)**: Measure information retrieval and RAG fidelity (Recall@K, Precision@K, MRR, Context Relevance, Groundedness/Faithfulness).
- **Safety & Guardrails (`guardrails.py`)**: Pre- and post-generation safety checks including PII masking, toxic content filtering, scope adherence, and hallucination tripwires.
- **Failure-Isolated Observability (`obs.py`)**: Tracing hooks and run telemetry (OpenTelemetry, Langfuse, Laminar) ensuring evaluation execution never halts on telemetry failures.
- **Reporting & Quality Gates (`report.py`)**: Export evaluations to Markdown tables, structured JSON, and terminal summaries with configurable pass/fail thresholds for CI.
- **Command-Line Interface (`cli.py`)**: Run evaluation suites and inspect regression reports directly from the terminal or GitHub Actions.

---

## Project Structure

```text
llm-eval-kit/
├── CHANGELOG.md
├── pyproject.toml
├── README.md
├── src/
│   └── llm_eval_kit/
│       ├── __init__.py           # Package exports & public API
│       ├── cli.py                # CLI commands (run, report, compare)
│       ├── golden.py             # Golden dataset schema and loader
│       ├── guardrails.py         # Safety, toxicity, PII, hallucination guards
│       ├── judge.py              # LLM-as-a-Judge harness & scoring rubrics
│       ├── metrics.py            # Quantitative & semantic evaluation metrics
│       ├── obs.py                # Telemetry, tracing, and metric collection
│       ├── py.typed              # PEP 561 type annotation marker
│       ├── report.py             # Markdown, JSON, and CLI report generators
│       └── retrieval_eval.py     # RAG context and retrieval metrics
└── tests/                        # Test suite & unit tests
```

---

## Installation

### From Source (Editable)

```bash
git clone https://github.com/Harini1911/llm-eval-kit.git
cd llm-eval-kit
pip install -e .
```

### With Optional Dependencies

```bash
# Core + LLM client integrations
pip install -e ".[llm]"

# Core + RAG & vector evaluation utilities
pip install -e ".[rag]"

# Full installation with development tools
pip install -e ".[dev]"
```

---

## Quickstart

### 1. Golden Dataset Management

Define and load ground truth evaluation test cases:

```python
from llm_eval_kit.golden import GoldenDataset, TestCase

dataset = GoldenDataset(
    name="customer-support-eval",
    test_cases=[
        TestCase(
            id="case-001",
            input="How do I reset my account password?",
            expected_output="Navigate to Settings > Security and click 'Reset Password'.",
            context=["Settings page contains account security controls."],
            metadata={"domain": "auth", "criticality": "high"},
        )
    ],
)

# Export or load from JSON / JSONL
dataset.to_jsonl("eval_golden.jsonl")
loaded_dataset = GoldenDataset.from_jsonl("eval_golden.jsonl")
```

### 2. Evaluating Responses with Metrics

Compute deterministic and semantic scores:

```python
from llm_eval_kit.metrics import (
    exact_match_score,
    semantic_similarity,
    token_efficiency_score,
)

candidate_response = "Go to Settings > Security to reset your password."
reference_response = "Navigate to Settings > Security and click 'Reset Password'."

sim_score = semantic_similarity(candidate_response, reference_response)
is_exact = exact_match_score(candidate_response, reference_response)

print(f"Semantic Similarity: {sim_score:.2f}")
print(f"Exact Match: {is_exact}")
```

### 3. LLM-as-a-Judge

Automate subjective grading with criteria rubrics:

```python
from llm_eval_kit.judge import LLMJudge, RubricCriteria

judge = LLMJudge(
    model="gpt-4o-mini",  # or local model endpoint
    criteria=[
        RubricCriteria.HELPFULNESS,
        RubricCriteria.ACCURACY,
        RubricCriteria.CONCISENESS,
    ],
)

result = judge.evaluate(
    prompt="Explain photosynthesis in two sentences.",
    response="Photosynthesis is how plants turn sunlight, water, and CO2 into sugar and oxygen. It powers plant growth.",
    expected="Plants convert sunlight into chemical energy producing oxygen.",
)

print(f"Score: {result.score}/5.0")
print(f"Reasoning: {result.rationale}")
```

### 4. RAG & Retrieval Assessment

Evaluate the context retrieved by your search or vector database:

```python
from llm_eval_kit.retrieval_eval import (
    evaluate_retrieval,
    hit_rate_at_k,
    mrr_at_k,
)

retrieved_doc_ids = ["doc_3", "doc_7", "doc_1", "doc_9"]
relevant_doc_ids = ["doc_1", "doc_4"]

hit = hit_rate_at_k(retrieved=retrieved_doc_ids, relevant=relevant_doc_ids, k=3)
mrr = mrr_at_k(retrieved=retrieved_doc_ids, relevant=relevant_doc_ids, k=3)

print(f"Hit@3: {hit}")
print(f"MRR@3: {mrr:.3f}")
```

### 5. Guardrails & Safety Checks

Validate outputs before serving to users:

```python
from llm_eval_kit.guardrails import GuardrailRunner, MaskPII, ToxicityCheck

guardrails = GuardrailRunner([
    MaskPII(),
    ToxicityCheck(threshold=0.8),
])

decision = guardrails.check(
    text="Contact me at support@example.com or call 555-0199."
)

if not decision.passed:
    print(f"Violations detected: {decision.violations}")
else:
    print("Sanitized text:", decision.sanitized_text)
```

### 6. Automated Reports & CI Quality Gates

Generate Markdown and JSON reports for pull requests:

```python
from llm_eval_kit.report import EvalReport, EvaluationRun

report = EvalReport.generate(
    suite_name="Regression-Suite-v1",
    runs=[...],
    thresholds={"semantic_similarity": 0.80, "safety_pass_rate": 1.0},
)

# Output GitHub-flavored markdown summary
markdown_output = report.to_markdown()
print(markdown_output)

# Check if CI should pass or fail
if not report.passed:
    raise SystemExit(1)
```

---

## CLI Usage

The package provides the `llm-eval-kit` command:

```bash
# Run evaluations against a golden dataset
llm-eval-kit run --dataset tests/data/golden.jsonl --output results.json

# Check thresholds for CI pipelines
llm-eval-kit check --results results.json --min-score 0.85

# Generate a formatted markdown summary report
llm-eval-kit report --results results.json --format markdown --out PR_SUMMARY.md
```

---

## CI/CD Integration Example

Add an evaluation gate to `.github/workflows/eval.yml`:

```yaml
name: LLM Regression & Evaluation

on:
  pull_request:
    branches: [main]

jobs:
  eval:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install dependencies
        run: |
          pip install -e ".[dev]"

      - name: Run Evaluation Suite
        run: |
          python -m llm_eval_kit.cli run \
            --dataset tests/data/golden.jsonl \
            --output eval-results.json \
            --fail-on-threshold

      - name: Post Eval Report to PR
        if: always()
        run: |
          python -m llm_eval_kit.cli report \
            --results eval-results.json \
            --format markdown >> $GITHUB_STEP_SUMMARY
```

---

## Development & Testing

```bash
# Run unit tests
pytest tests/ -v

# Type checking
mypy src/

# Linting & code style
ruff check src/
ruff format --check src/
```

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
