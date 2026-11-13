import json
import re

# Helper function to extract the final answer
def extract_answer(text):
    text_str = str(text)
    
    # Try the strict prompt format first
    strict_match = re.search(r"ANSWER:\s*(Yes|No|Abstain)", text_str, re.IGNORECASE)
    if strict_match:
        return strict_match.group(1).title()
        
    # Fallback for conversational models 
    # finds the last occurrence of the target words, ignoring punctuation
    fallback_match = re.findall(r"\b(Yes|No|Abstain)\b", text_str, re.IGNORECASE)
    if fallback_match:
        return fallback_match[-1].title()
        
    return "Invalid"

# Loading the results data
print("Loading experiment results...\n")
with open("experiment_results.json", "r") as f:
    data = json.load(f)

models = list(data[0]["models"].keys())
conditions = ["Baseline", "CoT", "Placebo", "PSV"]
total_pairs = len(data)

# set up the results table
print(f"{'Model':<30} | {'Condition':<10} | {'Solvable Attempt (A)':<20} | {'Abstention Acc (B)':<20} | {'False-Abstain (A)':<20} | {'Hallucination (B)':<20}")
print("-" * 135)

# Process and calculate metrics
for model in models:
    for condition in conditions:
        twin_a_attempted = 0      # Answered Yes/No on Solvable
        twin_a_false_abstain = 0  # Answered Abstain on Solvable
        twin_b_correct = 0        # Answered Abstain on Undetermined
        twin_b_hallucination = 0  # Answered Yes/No on Undetermined
        
        for pair in data:
            res_a = pair["models"][model][condition]["twin_a_solvable_response"]
            res_b = pair["models"][model][condition]["twin_b_undetermined_response"]
            
            ans_a = extract_answer(res_a)
            ans_b = extract_answer(res_b)
            
            # Twin A (Solvable) Metrics
            if ans_a in ["Yes", "No"]:
                twin_a_attempted += 1
            elif ans_a == "Abstain":
                twin_a_false_abstain += 1
                
            # Twin B (Undetermined) Metrics
            if ans_b == "Abstain":
                twin_b_correct += 1
            elif ans_b in ["Yes", "No"]:
                twin_b_hallucination += 1
                
        # Calculate percentages
        a_acc_pct = (twin_a_attempted / total_pairs) * 100
        b_acc_pct = (twin_b_correct / total_pairs) * 100
        fa_pct = (twin_a_false_abstain / total_pairs) * 100
        hal_pct = (twin_b_hallucination / total_pairs) * 100
        
        # Print row
        model_short = model.split("/")[-1]
        print(f"{model_short:<30} | {condition:<10} | {a_acc_pct:>18.1f}% | {b_acc_pct:>18.1f}% | {fa_pct:>18.1f}% | {hal_pct:>18.1f}%")
    print("-" * 135)