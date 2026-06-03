import json
import random


# LOAD DATASET

with open(
    "socratic_dataset.jsonl",
    "r"
) as f:
    lines = f.readlines()


# SETTINGS

VIEW_MODE = "random"      # random, early, middle, late
SAMPLE_SIZE = 50       # how many examples to show


# PICK EXAMPLES

if VIEW_MODE == "early":
    samples = lines[:SAMPLE_SIZE]

elif VIEW_MODE == "middle":
    middle = len(lines) // 2
    samples = lines[middle:middle + SAMPLE_SIZE]

elif VIEW_MODE == "late":
    samples = lines[-SAMPLE_SIZE:]

else:  # random
    samples = random.sample(lines, min(SAMPLE_SIZE, len(lines)))


# DISPLAY

for i, line in enumerate(samples):

    convo = json.loads(line)

    print("\n" + "=" * 60)

    print(f"EXAMPLE {i + 1}")

    print("=" * 60)

    print(f"\nTOPIC: {convo['topic']}")

    print(f"SUBJECT: {convo['subject']}")

    print(f"TURNS: {convo['turn_count']}")

    print("\nCONVERSATION:\n")

    for turn in convo["conversation"]:

        role = turn["role"]

        content = turn["content"]

        print(f"{role.upper()}: {content}\n")