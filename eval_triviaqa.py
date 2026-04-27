import requests
from datasets import load_dataset

API = "http://localhost:8000"
SAMPLE_SIZE = 100


def run_ask(question: str) -> dict:
    try:
        r = requests.post(f"{API}/ask", json={"question": question}, timeout=30)
        return r.json()
    except Exception as e:
        return {"decision": "error", "uncertainty_score": None, "error": str(e)}


def main():
    print("Loading trivia_qa dataset...")
    ds = load_dataset("trivia_qa", "rc", split=f"validation[:{SAMPLE_SIZE}]")
    print(f"Loaded {len(ds)} examples\n")

    results = []
    for i, row in enumerate(ds):
        question = row["question"]
        expected = "answer"  # trivia_qa questions are clear factual questions

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

    total = len(results)
    correct_count = sum(r["correct"] for r in results)
    match_pct = correct_count / total * 100

    print("=" * 50)
    print(f"Overall match:  {correct_count}/{total}  ({match_pct:.1f}%)")
    print(f"Answered directly (correct): {correct_count}")
    print(f"Asked clarification (wrong): {total - correct_count}")
    print("=" * 50)


if __name__ == "__main__":
    main()
