import json

from collections import Counter


# CREATE COUNTERS

topic_counter = Counter()

score_counter = Counter()


total_examples = 0


# OPEN CLEANED DATASET

with open(

    "socratic_dataset.jsonl",

    "r"

) as f:

    for line in f:

        item = json.loads(line)


        total_examples += 1


        # TOPIC COUNT

        topic_counter[item["topic"]] += 1


        # QUALITY SCORE COUNT

        score_counter[item["quality_score"]] += 1


# PRINT RESULTS

print("\nTOTAL EXAMPLES:\n")

print(total_examples)


print("\nTOPIC DISTRIBUTION:\n")

print(topic_counter)


print("\nQUALITY SCORE DISTRIBUTION:\n")

print(score_counter)