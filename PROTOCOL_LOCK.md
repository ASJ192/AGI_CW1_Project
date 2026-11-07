# Experimental Protocol Lock
**Timestamp:** November 7, 2026
**Researcher:** Amanveer Jagdey

## 1. Research Question
How does premise-sufficiency verification (PSV) affect correct abstention in LLMs on paired solvable and underdetermined deductive reasoning tasks?

## 2. Hypotheses
* **H1 (Alternative):** The PSV prompt will significantly increase correct abstention on underdetermined tasks without proportionally increasing false-abstention on solvable tasks, thereby improving overall paired accuracy compared to baseline.
* **H0 (Null):** The PSV prompt will have no significant effect on paired accuracy, or will degrade performance via over-conservative false-abstention.

## 3. Variables
* **Independent Variable:** Prompt Condition (Baseline, Chain-of-Thought, Placebo, PSV).
* **Dependent Variables:** Paired Accuracy (Primary), False-Abstention Rate, Fabrication Rate, Detection-to-Abstention Gap.

## 4. Methodology & Data
* **Dataset:** 50 procedurally generated deductive logic tasks (25 minimal pairs: 1 solvable, 1 underdetermined).
* **Environment:** API inference at Temperature 0.0 (Greedy decoding) to ensure deterministic reproducibility.

## 5. Main Threats to Validity
* **Construct Validity:** Small models may fail basic logic under heavy metacognitive prompting, registering as false-abstentions.
* **Mitigation:** Testing across multiple frontier model families to isolate architectural artifacts from genuine metacognitive failures.