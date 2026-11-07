import json

# Define the logical structures and their variations
templates = [
    {
        "rule": "Transitive",
        "expected_a": "Yes",
        "pairs": [
            ("bloops", "feps", "glops"), ("widgets", "sprockets", "cogs"), 
            ("ziks", "yaks", "wuks"), ("alpha nodes", "beta nodes", "gamma nodes"), 
            ("red quarks", "blue quarks", "green quarks")
        ],
        "format_a": ["All {0} are {1}.", "All {1} are {2}."],
        "format_b": ["All {0} are {1}."],
        "question": "Are all {0} {2}?"
    },
    {
        "rule": "Modus_Ponens",
        "expected_a": "Yes",
        "pairs": [
            ("it rains", "the grass is wet"), ("the server crashes", "the alarm sounds"),
            ("the temperature drops", "the pipes freeze"), ("the user clicks", "the page loads"),
            ("the battery dies", "the screen goes black")
        ],
        "format_a": ["If {0}, then {1}.", "It is true that {0}."],
        "format_b": ["If {0}, then {1}."],
        "question": "Is it true that {1}?"
    },
    {
        "rule": "Modus_Tollens",
        "expected_a": "No",
        "pairs": [
            ("the code compiles", "the syntax is correct"), ("the vault opens", "the passcode is valid"),
            ("the engine starts", "there is fuel"), ("the plant grows", "it receives sunlight"),
            ("the message sends", "the network is active")
        ],
        "format_a": ["If {0}, then {1}.", "It is not true that {1}."],
        "format_b": ["If {0}, then {1}."],
        "question": "Is it true that {0}?"
    },
    {
        "rule": "Disjunctive_Syllogism",
        "expected_a": "Yes",
        "pairs": [
            ("the key is in the drawer", "the key is on the table"), ("the signal is high", "the signal is low"),
            ("the package is in transit", "the package is delivered"), ("the suspect went left", "the suspect went right"),
            ("the data is cached", "the data is fetched live")
        ],
        "format_a": ["Either {0}, or {1}.", "It is not true that {0}."],
        "format_b": ["Either {0}, or {1}."],
        "question": "Is it true that {1}?"
    },
    {
        "rule": "Hypothetical_Syllogism",
        "expected_a": "Yes",
        "pairs": [
            ("A activates", "B activates", "C activates"), ("the price rises", "demand falls", "supply increases"),
            ("the switch is flipped", "the circuit closes", "the light turns on"), ("the wind blows", "the turbine spins", "power is generated"),
            ("the threshold is met", "the alert triggers", "the system halts")
        ],
        "format_a": ["If {0}, then {1}.", "If {1}, then {2}."],
        "format_b": ["If {0}, then {1}."],
        "question": "If {0}, is it true that {2}?"
    }
]

dataset = []
pair_id = 1

for temp in templates:
    for items in temp["pairs"]:
        # Twin A (Solvable)
        twin_a_premises = [f.format(*items) for f in temp["format_a"]]
        twin_a = {
            "premises": twin_a_premises,
            "question": temp["question"].format(*items),
            "expected": temp["expected_a"]
        }
        
        # Twin B (Undetermined)
        twin_b_premises = [f.format(*items) for f in temp["format_b"]]
        twin_b = {
            "premises": twin_b_premises,
            "question": temp["question"].format(*items),
            "expected": "Abstain"
        }
        
        dataset.append({
            "pair_id": pair_id,
            "logical_rule": temp["rule"],
            "twin_a_solvable": twin_a,
            "twin_b_undetermined": twin_b
        })
        pair_id += 1

# Save to a JSON file
with open("dataset.json", "w") as f:
    json.dump(dataset, f, indent=4)

print(f"Successfully generated {len(dataset)} minimal pairs (50 total questions) and saved to dataset.json.")