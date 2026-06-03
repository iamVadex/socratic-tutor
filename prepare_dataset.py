import json

INPUT_FILE = "socratic_dataset.jsonl"
OUTPUT_FILE = "train_dataset.jsonl"

SYSTEM_PROMPT = (
    "You are a Socratic tutor. "
    "Guide students using questions instead of giving direct answers."
)

training_examples = []

with open(INPUT_FILE, "r", encoding="utf-8") as f:

    for line in f:

        convo = json.loads(line)

        turns = convo["conversation"]

        for i in range(len(turns) - 1):

            current_turn = turns[i]
            next_turn = turns[i + 1]

            if (
                current_turn["role"] == "student"
                and next_turn["role"] == "tutor"
            ):

                example = {
                    "messages": [
                        {
                            "role": "system",
                            "content": SYSTEM_PROMPT
                        },
                        {
                            "role": "user",
                            "content": current_turn["content"]
                        },
                        {
                            "role": "assistant",
                            "content": next_turn["content"]
                        }
                    ]
                }

                training_examples.append(example)

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:

    for example in training_examples:

        f.write(json.dumps(example) + "\n")

print("Training examples:", len(training_examples))
print("Saved to:", OUTPUT_FILE)