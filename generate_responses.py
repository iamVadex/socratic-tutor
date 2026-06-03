import json
import ollama

def format_prompt(example):
    topic = example["topic"]
    subject = example["subject"]
    
    system = f"""You are a Socratic tutor teaching {subject}. Topic: {topic}.
NEVER give direct answers. ALWAYS respond with a guiding question that helps the student think deeper.
Do not explain or lecture. Only ask questions."""

    # Build conversation history
    history = ""
    for turn in example["conversation"]:
        role = turn["role"].upper()
        history += f"{role}: {turn['content']}\n"
    
    prompt = f"{system}\n\nConversation so far:\n{history}\nTUTOR:"
    return prompt

def generate_response(prompt, model_name):
    response = ollama.generate(
        model=model_name,
        prompt=prompt,
        options={"temperature": 0.7, "max_tokens": 200}
    )
    return response["response"].strip()

# Load test set
with open("test_set.jsonl", "r") as f:
    test_samples = [json.loads(line) for line in f]

results = []

for i, example in enumerate(test_samples):
    print(f"Processing {i+1}/50 — {example['topic']}")
    prompt = format_prompt(example)
    
    base_response = generate_response(prompt, "gemma2:9b")
    
    results.append({
        "id": i,
        "topic": example["topic"],
        "subject": example["subject"],
        "conversation": example["conversation"],
        "prompt": prompt,
        "base_response": base_response,
        "finetuned_response": None  # fill this on Kaggle
    })

with open("base_responses.json", "w") as f:
    json.dump(results, f, indent=2)

print("Done! Saved base_responses.json")