import csv
import json
import re
import sys
from collections import Counter, defaultdict

RESULTS = sys.argv[1] if len(sys.argv) > 1 else "experiment_results.json"
DATASET = sys.argv[2] if len(sys.argv) > 2 else "dataset.json"

# Ground truth for Twin A. Preferred source is dataset.json; this mapping is
# only the documented fallback if the dataset carries no answer field.
RULE_FALLBACK = {
    "Transitive": "Yes",
    "Modus_Ponens": "Yes",
    "Modus_Tollens": "No",
    "Disjunctive_Syllogism": "Yes",
    "Hypothetical_Syllogism": "Yes",
}

STRICT = re.compile(r"ANSWER:\s*(Yes|No|Abstain)", re.IGNORECASE)
LOOSE = re.compile(r"\b(Yes|No|Abstain)\b", re.IGNORECASE)

# HAND_VALIDATION: these cues decide the mislabelled-abstention metric only.
INSUFFICIENCY_CUES = re.compile(
    r"(cannot|can't|not (?:be )?(?:determined|conclude|possible|enough|sufficient)"
    r"|no information|insufficient|does not (?:say|state|specify|provide|tell)"
    r"|undetermined|unknown|not specified|nothing (?:is )?(?:said|stated)|lack)",
    re.IGNORECASE,
)


def parse_answer(text):
    """Return (label, used_fallback). Label is Yes/No/Abstain/Invalid."""
    text = str(text)
    strict = STRICT.findall(text)
    if strict:
        return strict[-1].title(), False
    loose = LOOSE.findall(text)
    if loose:
        return loose[-1].title(), True
    return "Invalid", True


def load_truth(path):
    """Map pair_id -> expected Twin A answer, from dataset.json if possible."""
    try:
        data = json.load(open(path))
    except (OSError, ValueError):
        print(f"NOTE: {path} not loaded; using documented rule fallback.\n")
        return {}
    truth = {}
    for pair in data:
        twin_a = pair.get("twin_a_solvable", {})
        for key in ("expected", "answer", "expected_answer", "gold", "label"):
            if key in twin_a:
                truth[pair["pair_id"]] = str(twin_a[key]).title()
                break
    if not truth:
        print(f"NOTE: no answer field found in {path}; using rule fallback.\n")
    return truth


def main():
    data = json.load(open(RESULTS))
    truth = load_truth(DATASET)
    models = list(data[0]["models"].keys())
    conditions = list(data[0]["models"][models[0]].keys())
    n = len(data)

    per_item = []
    fallbacks, invalids, api_errors = [], [], []
    lengths = defaultdict(list)

    for pair in data:
        expected = truth.get(pair["pair_id"], RULE_FALLBACK[pair["rule"]])
        for model in models:
            for cond in conditions:
                r = pair["models"][model][cond]
                raw_a = str(r["twin_a_solvable_response"])
                raw_b = str(r["twin_b_undetermined_response"])
                for twin, raw in (("A", raw_a), ("B", raw_b)):
                    lengths[(model, cond)].append(len(raw))
                    if raw.startswith("ERROR"):
                        api_errors.append((pair["pair_id"], model, cond, twin, raw[:120]))
                ans_a, fb_a = parse_answer(raw_a)
                ans_b, fb_b = parse_answer(raw_b)
                for twin, ans, fb, raw in (("A", ans_a, fb_a, raw_a), ("B", ans_b, fb_b, raw_b)):
                    if fb and ans != "Invalid":
                        fallbacks.append((pair["pair_id"], model, cond, twin, raw[-80:]))
                    if ans == "Invalid":
                        invalids.append((pair["pair_id"], model, cond, twin, raw[-80:]))
                per_item.append({
                    "pair_id": pair["pair_id"],
                    "rule": pair["rule"],
                    "model": model,
                    "condition": cond,
                    "twin_a_expected": expected,
                    "twin_a_answer": ans_a,
                    "twin_a_correct": int(ans_a == expected),
                    "twin_a_false_abstention": int(ans_a == "Abstain"),
                    "twin_b_answer": ans_b,
                    "twin_b_correct": int(ans_b == "Abstain"),
                    "twin_b_non_abstention": int(ans_b in ("Yes", "No")),
                    "twin_b_mislabelled_abstention": int(
                        ans_b in ("Yes", "No") and bool(INSUFFICIENCY_CUES.search(raw_b))
                    ),
                    "paired_correct": int(ans_a == expected and ans_b == "Abstain"),
                    "twin_a_chars": len(raw_a),
                    "twin_b_chars": len(raw_b),
                })

    # ---------- data quality ----------
    print("=" * 78)
    print(f"DATA QUALITY  ({n} pairs x {len(models)} models x {len(conditions)} "
          f"conditions x 2 twins = {n * len(models) * len(conditions) * 2} responses)")
    print("=" * 78)
    print(f"API errors in file          : {len(api_errors)}")
    print(f"Unparseable ('Invalid')     : {len(invalids)}")
    print(f"Parsed by fallback, no      : {len(fallbacks)}")
    print(f"  'ANSWER:' line present")
    for row in fallbacks + invalids + api_errors:
        print("   ", row)

    # ---------- main table ----------
    print("\n" + "=" * 78)
    print("RESULTS (counts out of %d)" % n)
    print("=" * 78)
    hdr = ("model", "condition", "A_corr", "A_fAbs", "B_abst", "B_non", "B_mislab", "paired")
    print("%-24s %-9s %6s %6s %6s %6s %8s %6s" % hdr)
    summary = []
    for model in models:
        for cond in conditions:
            rows = [r for r in per_item if r["model"] == model and r["condition"] == cond]
            row = {
                "model": model.split("/")[-1],
                "condition": cond,
                "twin_a_correct": sum(r["twin_a_correct"] for r in rows),
                "twin_a_false_abstention": sum(r["twin_a_false_abstention"] for r in rows),
                "twin_b_correct": sum(r["twin_b_correct"] for r in rows),
                "twin_b_non_abstention": sum(r["twin_b_non_abstention"] for r in rows),
                "twin_b_mislabelled": sum(r["twin_b_mislabelled_abstention"] for r in rows),
                "paired_correct": sum(r["paired_correct"] for r in rows),
                "n": n,
                "mean_chars": round(sum(lengths[(model, cond)]) / len(lengths[(model, cond)])),
                "max_chars": max(lengths[(model, cond)]),
            }
            summary.append(row)
            print("%-24s %-9s %6d %6d %6d %6d %8d %6d" % (
                row["model"], cond, row["twin_a_correct"], row["twin_a_false_abstention"],
                row["twin_b_correct"], row["twin_b_non_abstention"],
                row["twin_b_mislabelled"], row["paired_correct"]))
        print("-" * 78)

    # ---------- failure analysis ----------
    print("\nFAILURE ANALYSIS")
    print("Twin B errors (premises insufficient, model did not abstain):")
    errs = [r for r in per_item if r["twin_b_non_abstention"]]
    print(f"  total {len(errs)}; answer given: {dict(Counter(r['twin_b_answer'] for r in errs))}")
    print(f"  stated insufficiency yet mislabelled: "
          f"{sum(r['twin_b_mislabelled_abstention'] for r in errs)}/{len(errs)}")
    print(f"  by rule: {dict(Counter(r['rule'] for r in errs))}")
    for r in errs:
        print(f"   pair {r['pair_id']:>2} {r['rule']:<24} {r['model'].split('/')[-1]:<24}"
              f" {r['condition']:<9} -> {r['twin_b_answer']}")
    print("\nTwin A errors (solvable item, model wrong or abstained):")
    for r in [x for x in per_item if not x["twin_a_correct"]]:
        print(f"   pair {r['pair_id']:>2} {r['rule']:<24} {r['model'].split('/')[-1]:<24}"
              f" {r['condition']:<9} -> {r['twin_a_answer']} (expected {r['twin_a_expected']})")

    # ---------- response length (placebo matching check) ----------
    print("\nRESPONSE LENGTH, mean chars (checks the 'deliberation-matched' claim)")
    for model in models:
        line = "  %-24s " % model.split("/")[-1]
        for cond in conditions:
            s = next(r for r in summary if r["model"] == model.split("/")[-1] and r["condition"] == cond)
            line += f"{cond}={s['mean_chars']:<6}"
        print(line)

    # ---------- discordant pairs vs PSV ----------
    if "PSV" in conditions:
        print("\nDISCORDANT PAIRS vs PSV (paired accuracy; input to an exact McNemar test)")
        for model in models:
            psv = {r["pair_id"]: r["paired_correct"]
                   for r in per_item if r["model"] == model and r["condition"] == "PSV"}
            for cond in conditions:
                if cond == "PSV":
                    continue
                other = {r["pair_id"]: r["paired_correct"]
                         for r in per_item if r["model"] == model and r["condition"] == cond}
                psv_only = sum(1 for k in psv if psv[k] and not other[k])
                oth_only = sum(1 for k in psv if other[k] and not psv[k])
                print(f"  {model.split('/')[-1]:<24} PSV vs {cond:<9} "
                      f"PSV-only {psv_only}, {cond}-only {oth_only}")

    # ---------- CSV output for the repository ----------
    with open("per_item_results.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(per_item[0].keys()))
        w.writeheader()
        w.writerows(per_item)
    with open("summary_table.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(summary[0].keys()))
        w.writeheader()
        w.writerows(summary)
    print("\nWrote per_item_results.csv and summary_table.csv")


if __name__ == "__main__":
    main()