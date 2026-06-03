import json


# DUPLICATE TRACKER

seen = set()


# TOPIC KEYWORDS

topic_keywords = {

    "gravity": ["mass", "fall", "Earth", "gravity"],

    "Newton's laws": ["force", "motion", "acceleration"],

    "velocity": ["speed", "direction", "motion"],

    "momentum": ["mass", "speed", "momentum"],

    "friction": ["surface", "friction", "slow"],

    "circuits": ["current", "voltage", "electricity"],

    "kinetic energy": ["energy", "motion", "speed"],

    "algebra": ["equation", "variable", "x"],

    "fractions": ["fraction", "denominator", "numerator"],

    "geometry": ["shape", "angle", "line"],

    "triangles": ["triangle", "angle", "side"],

    "quadratic equations": ["quadratic", "roots", "x squared"]
}


# QUALITY SCORE FUNCTION

def quality_score(text, topic):

    score = 0


    # EXACTLY ONE QUESTION

    if text.count("?") == 1:
        score += 2


    # GOOD LENGTH

    words = len(text.split())

    if 10 <= words <= 40:
        score += 2


    # NO DIRECT ANSWERS

    banned_phrases = [

        "the answer is",

        "it is defined as",

        "formula is",

        "equals"
    ]

    bad = False

    for phrase in banned_phrases:

        if phrase in text.lower():
            bad = True

    if not bad:
        score += 2


    # TOPIC RELEVANCE

    keywords = topic_keywords.get(topic, [])

    if any(

        word.lower() in text.lower()

        for word in keywords
    ):

        score += 2


    return score


# CLEANED DATASET

cleaned = []


# READ DATASET

with open(

    "multi_turn_dataset_v2.jsonl",

    "r"

) as f:

    for line in f:

        item = json.loads(line)

        question = item["final_tutor_response"]

        topic = item["topic"]


        # REMOVE DUPLICATES

        if question in seen:
            continue

        seen.add(question)


        # CALCULATE SCORE

        score = quality_score(

            question,

            topic
        )


        # KEEP HIGH-QUALITY EXAMPLES

        if score >= 6:

            item["quality_score"] = score

            cleaned.append(item)


# SAVE CLEANED DATASET

with open(

    "cleaned_dataset.jsonl",

    "w"

) as f:

    for item in cleaned:

        f.write(

            json.dumps(item)

            + "\n"
        )


print("\nFiltering complete.")

print(f"Cleaned examples: {len(cleaned)}")