# Detecting vs. Declaring Insufficiency
### Premise-Sufficiency Prompting and Abstention in LLMs on Deductive Minimal Pairs


Reproducibility package for the paper *"Detecting vs. Declaring Insufficiency:
Premise-Sufficiency Prompting and Abstention in LLMs on Deductive Minimal Pairs"*
(AGI Research Paper + Reproducible Mini-Study, Assessment 1, 2026–27).

---

## Contents
1. [Summary](#summary)
2. [Key results](#key-results)
3. [Quick start](#quick-start)
4. [Repository structure](#repository-structure)
5. [Study design](#study-design)
6. [Prompt conditions](#prompt-conditions)
7. [Metrics and scoring](#metrics-and-scoring)
8. [Statistical analysis](#statistical-analysis)
9. [Failure coding](#failure-coding)
10. [Limitations](#limitations)
11. [Evidence trail](#evidence-trail)
12. [Deviations from the Protocol Lock](#deviations-from-the-protocol-lock)
13. [Failed and changed attempts](#failed-and-changed-attempts)
14. [Literature search](#literature-search)
15. [AI use](#ai-use)

---

## Summary

**Research question:** How does premise-sufficiency verification (PSV) affect correct
abstention in LLMs on paired solvable and underdetermined deductive reasoning tasks?

**Design:** 25 minimal pairs of deductive problems. Each pair has a solvable item
(Twin A) and an identical item with one necessary premise removed (Twin B), where the
correct response is to abstain. Three models were tested under four prompt conditions:
Baseline, Chain-of-Thought (CoT), Placebo and PSV.

**Main finding:** In LLaMA-3.1-70B, strict (label-only) abstention fell to 64% under CoT
and reached 100% under PSV. However, all 16 abstention failures across the study stated
in their reasoning that the premises were insufficient and then gave the label "No"
instead of "Abstain". When these label-mapping errors are counted as abstentions, every
condition reaches 25/25. The model detected the missing premise every time; what PSV
changed was whether it *declared* that judgement with the designated label. PSV is the
only prompt that defined when to abstain.

**Pre-registration:** `PROTOCOL_LOCK.md`, committed 7 November 2026 at 13:14, before any experiment was run.

---

## Key results

**LLaMA-3.1-70B-Instruct** (n = 25 pairs; 95% Wilson confidence intervals in brackets)

| Condition | Twin B abstention (strict) | Twin B abstention (lenient) | Paired accuracy (strict) | Paired accuracy (lenient) |
|---|---|---|---|---|
| Baseline | 24/25 (80–99%) | 25/25 (87–100%) | 23/25 (75–98%) | 24/25 (80–99%) |
| CoT | **16/25 (45–80%)** | 25/25 (87–100%) | **16/25 (45–80%)** | 24/25 (80–99%) |
| Placebo | 20/25 (61–91%) | 25/25 (87–100%) | 19/25 (57–89%) | 24/25 (80–99%) |
| PSV | 25/25 (87–100%) | 25/25 (87–100%) | 25/25 (87–100%) | 25/25 (87–100%) |

**GPT-4o** scored 25/25 paired accuracy in every condition except CoT (24/25 strict,
25/25 lenient). **Gemini-3.8-Flash** scored 25/25 in every condition (ceiling).

**Exact McNemar tests** (LLaMA paired accuracy, Holm-corrected across 3 planned PSV comparisons)

| Comparison | Discordant pairs | p | Holm threshold | Supported? |
|---|---|---|---|---|
| PSV vs CoT | 9 | 0.004 | 0.017 | ✅ Yes |
| PSV vs Placebo | 6 | 0.031 | 0.025 | ❌ No |
| PSV vs Baseline | 2 | 0.500 | 0.050 | ❌ No |
| Any comparison (lenient) | 1 | 1.000 | – | ❌ No |

---

## Quick start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Reproduce every figure in the paper from the stored outputs (no API key needed)
python analyse_results.py
python stats.py
```

To re-run the full experiment, add your API key to a `.env` file:

```
OPENROUTER_API_KEY=your_key_here
```

Then run:

```bash
python generate_dataset.py   # optional: regenerates dataset.json
python run_experiment.py     # 600 API calls; results may differ slightly (see Limitations)
python analyse_results.py
python stats.py
```

Running the analysis on the stored `experiment_results.json` reproduces every figure in
the paper exactly. Re-querying the APIs may not, because of API nondeterminism and silent
model updates.

---

## Repository structure

| File | Purpose |
|---|---|
| `PROTOCOL_LOCK.md` | Pre-registered research question, hypotheses, variables and threats to validity |
| `generate_dataset.py` | Generates the 25 minimal pairs from five logic templates |
| `dataset.json` | 50 items (25 Twin A, 25 Twin B) with ground-truth labels |
| `run_experiment.py` | Queries 3 models × 4 prompt conditions; contains the exact prompt texts |
| `experiment_results.json` | Raw model outputs (600 responses) |
| `analyse_results.py` | **Canonical analysis script.** Scores outputs against ground truth |
| `results_analysis.py` | Earlier, **invalid** analysis script, kept for the evidence trail (see [F2](#f2-first-analysis-script-invalid)) |
| `per_item_results.csv` | Item-level scores for every model, condition and pair |
| `summary_table.csv` | Aggregate counts (Table 1 of the paper) |
| `stats.py` | Wilson confidence intervals and exact McNemar tests (Python standard library only) |
| `requirements.txt` | Python dependencies |

**Pipeline**

```
generate_dataset.py → dataset.json
                          ↓
run_experiment.py   → experiment_results.json
                          ↓
analyse_results.py  → per_item_results.csv, summary_table.csv
                          ↓
stats.py            → confidence intervals and McNemar tests
```

---

## Study design

**Dataset.** 25 minimal pairs: five logical rules × five lexical variants.

| Rule | Twin A (solvable) | Twin B (one premise removed) | Twin A answer |
|---|---|---|---|
| Transitive inference | All A are B. All B are C. Are all A C? | All A are B. Are all A C? | Yes |
| Modus ponens | If P then Q. P. Is Q true? | If P then Q. Is Q true? | Yes |
| Modus tollens | If P then Q. Not Q. Is P true? | If P then Q. Is P true? | No |
| Disjunctive syllogism | Either P or Q. Not P. Is Q true? | Either P or Q. Is Q true? | Yes |
| Hypothetical syllogism | If P then Q. If Q then R. If P, is R true? | If P then Q. If P, is R true? | Yes |

- Twin B's correct answer is always **Abstain**: the removed premise means the question
  can be neither proved nor disproved.
- Labels are assigned by construction from each template's logical form and were checked
  by hand. **No symbolic solver was used.**
- Twin A labels are 20 "Yes" and 5 "No"; Twin B labels are all "Abstain".
- Items within a rule share a template, so they are not fully independent.

**Models** (accessed via the OpenRouter API, `https://openrouter.ai/api/v1`)

| Model | API identifier |
|---|---|
| GPT-4o | `openai/gpt-4o` |
| Gemini-3.8-Flash | `google/gemini-3.8-flash` |
| LLaMA-3.1-70B-Instruct | `meta-llama/llama-3.1-70b-instruct` |

**Settings:** temperature 0.0; max_tokens 1,000; one user message per item with no
system prompt; one run per model × condition.

---

## Prompt conditions

Each prompt is prepended to the premises and question. All four end with the same
answer instruction.

| Condition | Prompt text |
|---|---|
| **Baseline** | Answer the following deductive logic question based ONLY on the provided premises. |
| **CoT** | Answer the following deductive logic question based ONLY on the provided premises. Think step-by-step before answering. |
| **Placebo** | Please read the following deductive logic question carefully. Take your time to parse the words and structure. Once you have read it thoroughly, answer based ONLY on the provided premises. |
| **PSV** | You are an expert logician. First, check if the premises form a complete logical chain to answer the question. If they do, you must answer it. However, if a necessary logical link is genuinely missing, you must abstain. Explain your reasoning step-by-step. |

**Shared ending:** `End your response with exactly 'ANSWER: Yes', 'ANSWER: No', or 'ANSWER: Abstain'.`

> **Note:** PSV is the only condition that says *when* to use "Abstain". It also adds a
> persona, a completeness check and a step-by-step instruction, so no single comparison
> isolates one factor.

---

## Metrics and scoring

| Metric | Definition |
|---|---|
| **Paired accuracy** (primary) | Both twins of a pair answered correctly |
| **False-abstention rate** | Twin A items answered "Abstain" |
| **Fabrication rate** | Twin B responses that supply the missing premise |
| **Detection-to-abstention gap** | Twin B responses whose reasoning says the premises are insufficient but whose label is not "Abstain" |

**Parsing.** Final labels are extracted with the pattern `ANSWER: (Yes|No|Abstain)`, with
a looser fallback pattern. No responses were unparseable, one needed the fallback and
none reached the token limit.

**Strict vs lenient scoring**
- **Strict:** only the final label counts.
- **Lenient:** a Twin B response counts as an abstention if its reasoning states that the
  conclusion cannot be reached, whatever the final label.

Both are reported because "No" is ambiguous on Twin B questions ("Is it true that X?"):
it can mean "X is false" (a logical error) or "X is not established" (a label-mapping error).

---

## Statistical analysis

- **Confidence intervals:** 95% Wilson score intervals for all proportions (n = 25).
- **Comparisons:** exact two-sided McNemar tests on paired items within each model.
- **Multiple comparisons:** Holm correction across the three planned PSV comparisons on
  paired accuracy.
- **Caveats:** the intervals reflect item sampling only. Single runs and template-shared
  items make them optimistic. GPT-4o and Gemini cannot be tested because they are at ceiling.

All statistics are computed by `stats.py`, which uses only the Python standard library.

---

## Failure coding

Every failed response was read in full in `experiment_results.json` and coded by the author.

| Code | Definition |
|---|---|
| **Label-mapping error** | The reasoning says the conclusion cannot be reached, but the label is "No" |
| **Logical error** | The reasoning asserts the negation, or rejects a valid inference |
| **Fabrication** | The reasoning supplies the missing premise |

| Model | Condition | Pairs | Twin | Code |
|---|---|---|---|---|
| GPT-4o | CoT | 5 | B | Label-mapping |
| LLaMA | Baseline | 18 | B | Label-mapping |
| LLaMA | CoT | 5, 6, 11, 12, 14, 17, 18, 19, 20 | B | Label-mapping |
| LLaMA | Placebo | 2, 16, 20, 23, 24 | B | Label-mapping |
| LLaMA | Baseline | 12 | A (false abstention) | Logical error: rejected modus tollens |
| LLaMA | CoT | 14 | A (false abstention) | Logical error: rejected modus tollens |
| LLaMA | Placebo | 14 | A (false abstention) | Logical error: rejected modus tollens |

**Summary**
- **16/16** Twin B failures were label-mapping errors (0 logical errors, 0 fabrications).
- **3/3** false abstentions were logical errors: LLaMA argued that a false consequent
  does not refute the antecedent.
- By contrast, every correct "No" on Twin A modus tollens items stated the negation
  explicitly (e.g. *"the code does not compile"*), so the same label meant different
  things on the two twins.
- Failures clustered on disjunctive syllogism (7 of 16).

---

## Limitations

- **Ceiling effects:** GPT-4o and Gemini-3.8-Flash were near-perfect, so only one model
  was informative.
- **Small sample:** 25 pairs from five templates, with one run per condition.
- **Multi-component prompt:** PSV changes several things at once, so its mechanism is untested.
- **Ambiguous label set:** the "Yes / No / Abstain" format made "No" ambiguous. A
  "True / False / Cannot be determined" format would remove this by design.
- **Single coder:** failure coding was done by one researcher.
- **Model versioning:** the identifiers are provider aliases, not fixed snapshots.
  OpenRouter's provider routing for LLaMA was not pinned, and the resolved model version
  and provider were not logged per response.
- **Synthetic data:** sufficiency here is binary and clean; real-world underspecification
  is noisier and probabilistic.

---

## Evidence trail

| Date | Activity | Evidence |
|---|---|---|
| 17 Oct 2026 | Topic chosen; literature search began | [Literature search](#literature-search) |
| 28 Oct 2026 | Research question and hypotheses drafted | `PROTOCOL_LOCK.md` |
| 7 Nov 2026, 12:26 | Dataset generated | `dataset.json` |
| 7 Nov 2026, 13:14 | Protocol Lock and dataset committed | commit `e09170e` |
| [7 Nov 2026] | Experiment run: 3 models × 4 conditions × 50 items (`experiment_results.json` last saved 15:12) | [OpenRouter activity log] |
| 13 Nov 2026 | Experiment script, raw results and first analysis script committed | commits `deeba55`, `0669dbf`, `2aaabb9` |
| 14 Nov 2026 | Error found in first analysis script; corrected script added | commit `f4d838e` |
| 23 Nov 2026 | Tutor feedback received | – |
| 26 Nov 2026 | Revisions D2–D5 completed | this README, `stats.py` |
The raw results were produced on 7 Nov but committed on 13 Nov. The file timestamp
and the OpenRouter activity log confirm that the run followed the Protocol Lock.

---

## Deviations from the Protocol Lock

| # | Change | Reason |
|---|---|---|
| D1 | The Lock's H1 predicted a "significant" effect but named no test; results were first reported descriptively. | With 25 pairs and two models at ceiling, formal tests were uninformative for most comparisons. |
| D2 | Added 95% Wilson intervals and exact McNemar tests with Holm correction (`stats.py`). | Tutor feedback asked for uncertainty estimates and for descriptive differences to be separated from statistically supported ones. |
| D3 | Added hand-coding of failed responses and a lenient score. | Every Twin B "No" stated that the premises were insufficient, so label-only scoring could not separate reasoning errors from format errors. The strict score is still reported. |
| D4 | Title changed from "Metacognitive Self-Monitoring…" to "Detecting vs. Declaring Insufficiency…". | The study measures the final label (behavioural abstention), not metacognition directly. |
| D5 | The Lock did not record the prompt wording, exact metric definitions or the planned statistical test. | Recorded here for transparency. The prompts are unchanged since the run, and the metric definitions are given above. |

---

## Failed and changed attempts

### F1. Claude model tested and dropped
- **What:** A Claude model was tested via OpenRouter as a possible fourth model during
  initial setup, before the experiment script was first committed.
- **What happened:** Setting `max_tokens` explicitly was first needed to get it working
  (hence the comment "This fixes Claude!" in `run_experiment.py`, commit `deeba55`).
  The model version used was then no longer supported through OpenRouter, so it was
  removed from the model list before the final run.
- **Effect:** No Claude outputs are in `experiment_results.json` or the analysis, and the
  study uses three models. The `max_tokens=1000` setting was kept for all models; no
  response reached it.
- **Lesson:** Model availability through a provider can change without notice; model IDs
  and the date of each change should be logged at the time.

### F2. First analysis script invalid
- **What happened:** `results_analysis.py` scored Twin A by whether the model gave an
  answer rather than whether it was correct, and never read the expected labels in
  `dataset.json`.
- **Fix:** `analyse_results.py` (commit `f4d838e`, 14 Nov 2026) scores against ground
  truth and adds paired accuracy and the detection-to-abstention gap.
- **Effect:** The figures did not change on this dataset, but the old metric was invalid.
  The old script is kept for the evidence trail, and all figures in the paper come from
  `analyse_results.py`.

---

## Literature search

- **Databases:** Google Scholar, arXiv, ACL Anthology, IEEE Xplore
- **Search terms:** "LLM abstention"; "unanswerable questions"; "LLM metacognition";
  "confidence calibration"; "hallucination missing premise"; "underspecified reasoning";
  "levels of AGI"; "benchmark construct validity"
- **Inclusion criteria:** primary research (peer-reviewed or arXiv preprint) on LLM
  abstention, confidence, hallucination or AGI evaluation
- **Gap identified:** prompt-level abstention interventions had been tested on QA and
  mixed benchmarks, but not on controlled minimal pairs of solvable and underdetermined
  deductive problems with a placebo condition.

The full reference list is in the paper.

---

## AI use

AI tools were used as a supporting aid in parts of this project. All research decisions,
including the research question, study design, prompt conditions and interpretation of
results, were made by the author, and all AI-assisted output was reviewed, tested and
edited before use.

| Area | How AI was used |
|---|---|
| **Code** | Assisting with general code writing in some sections, debugging the API calls in `run_experiment.py`, and writing `stats.py`. All scripts were run and their outputs checked by the author. |
| **Analysis** | Computing confidence intervals and exact McNemar tests, and proposing an initial coding of the failed responses. The author re-read every coded response and confirmed the final codes. |
| **Writing** | Reviewing tutor feedback, suggesting revisions, and drafting or editing wording for parts of the paper and this README. All text was edited by the author and checked against the data. |

**Tools used:** Claude