"""
Run Deepeval against hard-coded single-turn LangGraph scenarios.

This script:
1. Builds the LangGraph workflow locally (no FastAPI server required).
2. Executes the graph for each case defined in `single_turn_cases.py`.
3. Wraps the resulting text in Deepeval `LLMTestCase`s.
4. Scores them with lightweight correctness/relevancy metrics.

Environment:
    OPENAI_API_KEY (required by Deepeval metrics)
    CONFIDENT_API_KEY (optional, unlocks hosted reporting)
    NETMIND_API_KEY or built-in constant for suggestion/critic LLM calls
"""

from __future__ import annotations

import json
import sys
from typing import List

from deepeval import evaluate
from deepeval.metrics import AnswerRelevancyMetric, GEval
from deepeval.test_case import LLMTestCase, LLMTestCaseParams

from langgraph_app import create_graph
from nodes import GraphState

from evals.single_turn_cases import SINGLE_TURN_CASES


def _extract_output(final_state: GraphState) -> str:
    """
    Determine which field best represents the LLM response for evaluation.

    Priority:
        1. `response` from the critic node (includes approvals & critiques).
        2. `critique` text if available.
        3. stringified `suggestion` payload.
        4. Raw JSON dump of the state as a fallback.
    """
    response = final_state.get("response")
    if isinstance(response, str) and response.strip():
        return response

    critique = final_state.get("critique")
    if isinstance(critique, str) and critique.strip():
        return critique

    suggestion = final_state.get("suggestion")
    if isinstance(suggestion, str) and suggestion.strip():
        return suggestion
    if isinstance(suggestion, dict):
        return json.dumps(suggestion)

    return json.dumps(final_state)


def _build_test_cases(app) -> List[LLMTestCase]:
    """Execute each scenario and convert the output into a Deepeval test case."""
    test_cases: List[LLMTestCase] = []

    for case in SINGLE_TURN_CASES:
        final_state = app.invoke(case["initial_state"])
        output_text = _extract_output(final_state)

        test_cases.append(
            LLMTestCase(
                input=case["description"],
                actual_output=output_text,
                expected_output=case["expected_outcome"],
                context=[case["description"]],
                retrieval_context=[
                    "LangGraph biohacker pipeline should tie advice to biomarker and wearable data."
                ],
            )
        )

    return test_cases


def main() -> None:
    """Entry point for CLI usage."""
    app = create_graph()
    test_cases = _build_test_cases(app)

    if not test_cases:
        print("No evaluation cases were built. Nothing to do.", file=sys.stderr)
        sys.exit(1)

    metrics = [
        AnswerRelevancyMetric(threshold=0.3),
        GEval(
            name="Behavioral-Expectation",
            criteria="Check whether the response references the biomarkers and wearable context described in the expected outcome.",
            evaluation_params=[LLMTestCaseParams.ACTUAL_OUTPUT, LLMTestCaseParams.EXPECTED_OUTPUT],
            threshold=0.3,
        ),
    ]

    # Raises if metrics fail. Deepeval also prints a summary table for local runs.
    evaluate(test_cases=test_cases, metrics=metrics)


if __name__ == "__main__":
    main()


