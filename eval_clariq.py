import pandas as pd
import requests

API = "http://localhost:8000"

# clarification_need: 1-2 = answer directly, 3-4 = ask clarifying question
CLARIFY_THRESHOLD = 3


def run_ask(question: str) -> dict:
    try:
        r = requests.post(f"{API}/ask", json={"question": question}, timeout=30)
        return r.json()
    except Exception as e:
        return {"decision": "error", "uncertainty_score": None, "error": str(e)}


def main():
    print("Loading ClariQ dataset from GitHub...")
    df = pd.read_csv(
        "https://raw.githubusercontent.com/aliannejadi/ClariQ/master/data/train.tsv",
        sep="\t",
    )
    # one row per unique question
    df = df.drop_duplicates(subset="initial_request").reset_index(drop=True)
    print(f"Loaded {len(df)} unique questions\n")

    results = []
    for i, row in df.iterrows():
        question = row["initial_request"]
        need = row["clarification_need"]
        expected = "clarify" if need >= CLARIFY_THRESHOLD else "answer"

        print(f"[{i+1}/{len(df)}] (need={need}) {question[:80]}")
        out = run_ask(question)

        got = out.get("decision", "error")
        score = out.get("uncertainty_score")
        correct = got == expected

        results.append({
            "question": question,
            "clarification_need": need,
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

    clarify_rows = [r for r in results if r["expected"] == "clarify"]
    answer_rows  = [r for r in results if r["expected"] == "answer"]

    clarify_acc = sum(r["correct"] for r in clarify_rows) / len(clarify_rows) * 100 if clarify_rows else 0
    answer_acc  = sum(r["correct"] for r in answer_rows)  / len(answer_rows)  * 100 if answer_rows  else 0

    tp = sum(1 for r in results if r["expected"] == "clarify" and r["got"] == "clarify")
    fp = sum(1 for r in results if r["expected"] == "answer"  and r["got"] == "clarify")
    fn = sum(1 for r in results if r["expected"] == "clarify" and r["got"] == "answer")

    precision = tp / (tp + fp) if (tp + fp) else 0
    recall    = tp / (tp + fn) if (tp + fn) else 0
    f1        = 2 * precision * recall / (precision + recall) if (precision + recall) else 0

    print("=" * 50)
    print(f"Overall match:       {correct_count}/{total}  ({match_pct:.1f}%)")
    print(f"Should clarify:      {sum(r['correct'] for r in clarify_rows)}/{len(clarify_rows)}  ({clarify_acc:.1f}%)")
    print(f"Should answer:       {sum(r['correct'] for r in answer_rows)}/{len(answer_rows)}  ({answer_acc:.1f}%)")
    print(f"Precision:           {precision:.2f}")
    print(f"Recall:              {recall:.2f}")
    print(f"F1:                  {f1:.2f}")
    print("=" * 50)


if __name__ == "__main__":
    main()
