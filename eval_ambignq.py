import requests
from datasets import load_dataset

API = "http://localhost:8000"
SAMPLE_SIZE = 100  # increase for more thorough eval, decrease to run faster


def run_ask(question: str) -> dict:
    try:
        r = requests.post(f"{API}/ask", json={"question": question}, timeout=30)
        return r.json()
    except Exception as e:
        return {"decision": "error", "uncertainty_score": None, "error": str(e)}


def main():
    print("Loading dataset...")
    ds = load_dataset("erbacher/AmbigNQ-clarifying-question", split=f"test[:{SAMPLE_SIZE}]")
    print(f"Loaded {len(ds)} examples\n")

    results = []
    for i, row in enumerate(ds):
        question = row["question"]
        expected = "clarify" if row["ambig"] else "answer"

        print(f"[{i+1}/{len(ds)}] {question[:80]}")
        out = run_ask(question)

        got = out.get("decision", "error")
        score = out.get("uncertainty_score")
        correct = got == expected

        results.append({
            "question": question,
            "expected": expected,
            "got": got,
            "score": score,
            "correct": correct,
        })

        status = "PASS" if correct else "FAIL"
        print(f"  {status}  expected={expected}  got={got}  uncertainty={score}\n")

    # summary
    total = len(results)
    correct_count = sum(r["correct"] for r in results)
    match_pct = correct_count / total * 100

    clarify_rows = [r for r in results if r["expected"] == "clarify"]
    answer_rows  = [r for r in results if r["expected"] == "answer"]

    clarify_acc = sum(r["correct"] for r in clarify_rows) / len(clarify_rows) * 100 if clarify_rows else 0
    answer_acc  = sum(r["correct"] for r in answer_rows)  / len(answer_rows)  * 100 if answer_rows  else 0

    print("=" * 50)
    print(f"Overall match:      {correct_count}/{total}  ({match_pct:.1f}%)")
    print(f"Ambiguous (clarify): {sum(r['correct'] for r in clarify_rows)}/{len(clarify_rows)}  ({clarify_acc:.1f}%)")
    print(f"Clear (answer):      {sum(r['correct'] for r in answer_rows)}/{len(answer_rows)}  ({answer_acc:.1f}%)")
    print("=" * 50)


if __name__ == "__main__":
    main()
