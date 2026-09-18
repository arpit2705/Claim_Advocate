"""
eval_runner.py — Runs hand-written scenarios and reports real accuracy.
"""
import sys
from datetime import date
import os
from typing import Any

# Ensure we can import app modules when running as a script
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from app.eval.scenarios import READINESS_SCENARIOS, ADJUDICATION_SCENARIOS, ADJUDICATION_CLAUSES
from app.modules.readiness_engine import run_readiness_pipeline
from app.modules.adjudication_engine import run_adjudication_pipeline
from app.retrieval.embedding_index import ClauseEmbeddingIndex
from app.retrieval.hybrid_retrieval import HybridRetriever
from app.config import GROQ_API_KEY


def run_readiness_eval():
    print("--- Evaluating Module A (Readiness) ---")
    correct = 0
    total = len(READINESS_SCENARIOS)

    for i, scenario in enumerate(READINESS_SCENARIOS):
        # Convert string dates to datetime.date for rule inputs
        rule_inputs = []
        for r in scenario["rule_inputs"]:
            mod_r = dict(r)
            if "incident_date" in mod_r:
                mod_r["incident_date"] = date.fromisoformat(mod_r["incident_date"])
            if "submission_date" in mod_r:
                mod_r["submission_date"] = date.fromisoformat(mod_r["submission_date"])
            rule_inputs.append(mod_r)

        result = run_readiness_pipeline(
            submission=scenario["input"],
            rule_inputs=rule_inputs,
            required_fields=scenario["required_fields"]
        )

        passed = True
        if "expected_min_score" in scenario and result.readiness_score < scenario["expected_min_score"]:
            passed = False
        if "expected_max_score" in scenario and result.readiness_score > scenario["expected_max_score"]:
            passed = False

        if passed:
            correct += 1
            print(f"[PASS] {scenario['name']} (Score: {result.readiness_score})")
        else:
            print(f"[FAIL] {scenario['name']} (Score: {result.readiness_score})")

    accuracy = (correct / total) * 100
    print(f"Module A Accuracy: {accuracy:.1f}% ({correct}/{total})\n")


def run_adjudication_eval():
    print("--- Evaluating Module B (Adjudication) ---")
    if not GROQ_API_KEY:
        print("[WARNING] GROQ_API_KEY not set. LLM-based adjudication cannot run. Skipping.")
        return

    # Initialize Retrieval
    idx = ClauseEmbeddingIndex()
    idx.build(ADJUDICATION_CLAUSES)
    retriever = HybridRetriever(idx)

    correct = 0
    total = len(ADJUDICATION_SCENARIOS)

    for i, scenario in enumerate(ADJUDICATION_SCENARIOS):
        result = run_adjudication_pipeline(
            rejection=scenario["input"],
            retriever=retriever
        )

        if result.verdict.verdict in scenario["expected_verdicts"]:
            correct += 1
            print(f"[PASS] {scenario['name']} (Verdict: {result.verdict.verdict})")
        else:
            print(f"[FAIL] {scenario['name']} (Expected: {scenario['expected_verdicts']}, Got: {result.verdict.verdict})")

    accuracy = (correct / total) * 100
    print(f"Module B Accuracy: {accuracy:.1f}% ({correct}/{total})\n")


if __name__ == "__main__":
    print("Starting Claim Advocate Evaluation Harness...\n")
    run_readiness_eval()
    run_adjudication_eval()
