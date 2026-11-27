import json
import os
from openai import OpenAI

# API Setup
from dotenv import load_dotenv

load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)

# The Models
MODELS = [
    "openai/gpt-4o",
    "google/gemini-3.8-flash",
    "meta-llama/llama-3.1-70b-instruct"
]

# The Prompt Conditions
PROMPTS = {
    "Baseline": "Answer the following deductive logic question based ONLY on the provided premises. End your response with exactly 'ANSWER: Yes', 'ANSWER: No', or 'ANSWER: Abstain'.\n\n",
    "CoT": "Answer the following deductive logic question based ONLY on the provided premises. Think step-by-step before answering. End your response with exactly 'ANSWER: Yes', 'ANSWER: No', or 'ANSWER: Abstain'.\n\n",
    "Placebo": "Please read the following deductive logic question carefully. Take your time to parse the words and structure. Once you have read it thoroughly, answer based ONLY on the provided premises. End your response with exactly 'ANSWER: Yes', 'ANSWER: No', or 'ANSWER: Abstain'.\n\n",
    "PSV": "You are an expert logician. First, check if the premises form a complete logical chain to answer the question. If they do, you must answer it. However, if a necessary logical link is genuinely missing, you must abstain. Explain your reasoning step-by-step. End your response with exactly 'ANSWER: Yes', 'ANSWER: No', or 'ANSWER: Abstain'.\n\n"
}

# Loading the Full Dataset
print("Loading dataset...")
with open("dataset.json", "r") as f:
    full_dataset = json.load(f)

def ask_model(model_id, prompt_text, puzzle_text):
    full_content = prompt_text + puzzle_text
    try:
        response = client.chat.completions.create(
            model=model_id,
            messages=[{"role": "user", "content": full_content}],
            temperature=0.0,
            max_tokens=1000 
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"ERROR: {str(e)}"

# TheFull Experiment
results = []
total_pairs = len(full_dataset)

for i, pair in enumerate(full_dataset, 1):
    print(f"\n--- Processing Pair {i}/{total_pairs}: {pair['logical_rule']} ---")
    
    puzzle_a = "Premises:\n" + "\n".join(pair['twin_a_solvable']['premises']) + "\nQuestion: " + pair['twin_a_solvable']['question']
    puzzle_b = "Premises:\n" + "\n".join(pair['twin_b_undetermined']['premises']) + "\nQuestion: " + pair['twin_b_undetermined']['question']
    
    pair_results = {"pair_id": pair["pair_id"], "rule": pair["logical_rule"], "models": {}}
    
    for model in MODELS:
        print(f"  Querying {model.split('/')[-1]}...")
        pair_results["models"][model] = {}
        for condition, prompt in PROMPTS.items():
            ans_a = ask_model(model, prompt, puzzle_a)
            ans_b = ask_model(model, prompt, puzzle_b)
            pair_results["models"][model][condition] = {
                "twin_a_solvable_response": ans_a,
                "twin_b_undetermined_response": ans_b
            }
            
    results.append(pair_results)

# Saving the Final Results
with open("experiment_results.json", "w") as f:
    json.dump(results, f, indent=4)

print("\nSUCCESS: All 50 questions processed and saved to experiment_results.json!")