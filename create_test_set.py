import json
import random

with open("socratic_dataset.jsonl", "r") as f:
    data = [json.loads(line) for line in f]

random.seed(42)
test_samples = random.sample(data, 50)

with open("test_set.jsonl", "w") as f:
    for item in test_samples:
        json.dump(item, f)
        f.write("\n")

print(f"Saved {len(test_samples)} examples")