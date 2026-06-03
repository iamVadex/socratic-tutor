import requests
import json
import random
import re
import time
from difflib import SequenceMatcher


# ============================================
# TUTOR SYSTEM PROMPT
# ============================================

TUTOR_SYSTEM_PROMPT = """You are a Socratic tutor. Your job is to guide students to discover answers themselves.

RULES — follow every one, no exceptions:
1. First reply: one short casual sentence framing the topic, then exactly ONE question. Nothing more.
2. Later replies: max 2 sentences. One question at the end. Never two questions.
3. Never state the answer, formula, or mechanism before the student reaches it.
4. Never list ingredients, steps, or components upfront.
5. No bullet points, no numbered lists, no headers.
6. If student is wrong: ask a simpler redirecting question. Do not explain why they are wrong.
7. If you see [HINT] in the message: give one short hint starting with "Hint:" then ask one question.
8. If you see [REVEAL] in the message: state that one piece of the answer, then ask the next question.
9. When the student correctly states the core concept or formula: confirm with one short sentence like "Exactly, you got it." and STOP. Do not ask another question.
10. Keep tone warm and curious. Short replies only.

CORRECT EXAMPLE:
Student: what is Newton's second law?
Tutor: Newton's second law connects force, mass, and acceleration. If you push a heavy and a light object with equal force, which moves more?
Student: the light one
Tutor: Right. Same object, push harder — what happens to its acceleration?
Student: it increases
Tutor: Exactly. So force increases acceleration, mass decreases it. Can you write that as a formula?
Student: F = ma?
Tutor: That's it. You derived it yourself.

WRONG EXAMPLES — never do these:
- Tutor: Photosynthesis uses sunlight, carbon dioxide, and water to produce glucose and oxygen. [gives answer upfront]
- Tutor: What keeps us in space? And what happens when you jump? [two questions]
- Tutor: This is a physics topic. What do you know? [robotic opener]
- Tutor: The answer is F = ma, which means force equals mass times acceleration. [states answer directly]
"""


# ============================================
# STUDENT SYSTEM PROMPT
# ============================================

STUDENT_SYSTEM_PROMPT = """You are a high school student hearing about this topic for the first time.

RULES:
1. Reply in ONE short sentence — usually just a few words.
2. Be partially right, wrong, or confused sometimes. Never perfectly correct unless guided there step by step.
3. Use casual language: idk, maybe, i think, oh wait, hmm.
4. Never repeat a phrase you already used in this conversation.
5. Never start with "Tutor:", "User:", "Student:", or "The tutor just said".
6. Occasionally show a small breakthrough: "oh wait that makes sense" or "ohh so its like..."

GOOD replies: "the heavy one i think?" / "idk maybe distance?" / "hmm not sure" / "oh wait so they balance?"
BAD replies: "The acceleration is inversely proportional to mass." / "Tutor: ..." / "The tutor just said..."
"""


# ============================================
# TOPICS
# ============================================

topics = [
    {
        "topic": "gravitational force",
        "subject": "physics", "difficulty": "beginner", "turns": 10,
        "answer_keywords": ["f = g", "gm1m2", "gravitational constant", "inverse square law"]
    },
    {
        "topic": "Newton's second law",
        "subject": "physics", "difficulty": "intermediate", "turns": 8,
        "answer_keywords": ["f = ma", "f=ma", "force equals mass times"]
    },
    {
        "topic": "Newton's third law",
        "subject": "physics", "difficulty": "beginner", "turns": 6,
        "answer_keywords": ["equal and opposite", "for every action there is", "action and reaction"]
    },
    {
        "topic": "momentum",
        "subject": "physics", "difficulty": "intermediate", "turns": 7,
        "answer_keywords": ["p = mv", "p=mv", "mass times velocity"]
    },
    {
        "topic": "Ohm's law",
        "subject": "physics", "difficulty": "intermediate", "turns": 7,
        "answer_keywords": ["v = ir", "v=ir", "voltage equals current times"]
    },
    {
        "topic": "kinetic and potential energy",
        "subject": "physics", "difficulty": "beginner", "turns": 8,
        "answer_keywords": ["ke = 1/2", "0.5 mv", "mgh", "potential energy equals mgh"]
    },
    {
        "topic": "osmosis",
        "subject": "biology", "difficulty": "beginner", "turns": 7,
        "answer_keywords": ["semi-permeable membrane", "high concentration to low", "solute concentration difference"]
    },
    {
        "topic": "photosynthesis",
        "subject": "biology", "difficulty": "beginner", "turns": 6,
        "answer_keywords": ["sunlight, carbon dioxide, and water", "co2 + h2o", "glucose and oxygen"]
    },
    {
        "topic": "DNA and protein synthesis",
        "subject": "biology", "difficulty": "advanced", "turns": 10,
        "answer_keywords": ["transcription and translation", "ribosome reads mrna", "mrna carries the code"]
    },
    {
        "topic": "natural selection",
        "subject": "biology", "difficulty": "intermediate", "turns": 9,
        "answer_keywords": [
            "survival of the fittest", "traits are passed on", "better adapted survive and reproduce",
            "leads to a population", "over time this leads", "passed on to future generations"
        ]
    },
    {
        "topic": "quadratic equations",
        "subject": "math", "difficulty": "intermediate", "turns": 8,
        "answer_keywords": ["ax^2 + bx + c", "quadratic formula", "x = -b"]
    },
    {
        "topic": "Pythagorean theorem",
        "subject": "math", "difficulty": "beginner", "turns": 6,
        "answer_keywords": ["a^2 + b^2 = c^2", "a squared plus b squared", "hypotenuse squared"]
    },
    {
        "topic": "supply and demand",
        "subject": "economics", "difficulty": "beginner", "turns": 6,
        "answer_keywords": ["equilibrium price", "supply equals demand"]
    },
    {
        "topic": "fractions and division",
        "subject": "math", "difficulty": "beginner", "turns": 6,
        "answer_keywords": ["numerator over denominator", "divide by multiplying by reciprocal"]
    },
    {
        "topic": "recursion",
        "subject": "computer science", "difficulty": "advanced", "turns": 9,
        "answer_keywords": ["base case stops", "function calls itself", "call stack"]
    },
]


# ============================================
# TOPIC GUIDE — steers tutor toward the right path
# ============================================

TOPIC_GUIDE = {
    "gravitational force":         "Steps: both masses matter → distance matters → distance is squared → F = Gm1m2/r^2.",
    "Newton's second law":         "Steps: heavier = less acceleration → push harder = more acceleration → a = F/m → F = ma.",
    "Newton's third law":          "Steps: push examples → rocket/ball → equal force both ways → every action has equal opposite reaction.",
    "momentum":                    "Steps: heavy things hit harder → speed matters too → p = mv.",
    "Ohm's law":                   "Steps: more voltage = more current → resistance fights current → V = IR.",
    "kinetic and potential energy": "Steps: moving things have energy (KE) → height stores energy (PE) → KE=1/2mv^2, PE=mgh → conversion between them.",
    "osmosis":                     "Steps: concentration difference → membrane lets water through not solute → water moves low to high solute → equilibrium.",
    "photosynthesis":              "Steps: water → CO2 from air → sunlight as energy source → outputs are glucose and oxygen.",
    "DNA and protein synthesis":   "Steps: DNA stays in nucleus → mRNA copies it (transcription) → ribosome reads mRNA (translation) → protein built.",
    "natural selection":           "Steps: variation exists → some traits help survival → those individuals reproduce more → traits spread over generations.",
    "quadratic equations":         "Steps: what makes it quadratic (x^2 term) → standard form ax^2+bx+c=0 → finding roots by factoring or formula.",
    "Pythagorean theorem":         "Steps: right triangle has 3 sides → square the two short sides → they add up to square of hypotenuse → a^2+b^2=c^2.",
    "supply and demand":           "Steps: scarcity raises price → surplus lowers price → balance point is equilibrium price.",
    "fractions and division":      "Steps: fraction means parts of a whole → numerator over denominator → dividing = multiplying by reciprocal.",
    "recursion":                   "Steps: function can call itself → risk of infinite loop → base case stops it → call stack builds up.",
}


# ============================================
# QUESTION TYPES
# ============================================

QUESTION_TYPES = [
    "probing_assumptions", "clarifying", "probing_evidence",
    "exploring_implications", "hypothetical", "meta"
]

def tag_question_type(text):
    t = text.lower()
    if any(w in t for w in ["what do you mean", "can you clarify", "what exactly"]):
        return "clarifying"
    if any(w in t for w in ["what are you assuming", "why do you think", "what makes you say"]):
        return "probing_assumptions"
    if any(w in t for w in ["how do you know", "what evidence", "what tells you"]):
        return "probing_evidence"
    if any(w in t for w in ["what would happen", "what if", "suppose", "imagine if", "if you"]):
        return "hypothetical"
    if any(w in t for w in ["what follows", "what does that mean", "so then", "if that's true"]):
        return "exploring_implications"
    if any(w in t for w in ["why is this important", "why does this matter"]):
        return "meta"
    return "hypothetical"


# ============================================
# CONVERSATION STARTERS
# ============================================

conversation_starters = [
    "what is {topic}?",
    "can you help me understand {topic}?",
    "i dont really get {topic}",
    "how does {topic} work?",
    "explain {topic} to me",
    "what's the formula for {topic}?",
    "why does {topic} happen?",
    "i have a doubt about {topic}",
]


# ============================================
# OLLAMA CALL  —  model: gemma2:9b
# ============================================

def call_ollama(messages, system_prompt):
    try:
        response = requests.post(
            "http://localhost:11434/api/chat",
            json={
                "model": "gemma2:9b",
                "stream": False,
                "options": {"temperature": 0.7},
                "messages": [
                    {"role": "user", "content": f"[SYSTEM INSTRUCTIONS]\n{system_prompt}\n[END INSTRUCTIONS]\n\nNow begin."},
                    {"role": "assistant", "content": "Understood. I will follow all instructions exactly."},
                    *messages
                ]
            },
            timeout=120
        )
        response.raise_for_status()
        return response.json()["message"]["content"].strip()
    except Exception as e:
        print(f"  [ERROR] {e}")
        return None


# ============================================
# QUALITY FILTERS
# ============================================

ANSWER_GIVEAWAY_PHRASES = [
    "the answer is", "the formula is", "can be written as", "is given by",
    "is defined as", "the equation is", "in summary", "to summarize",
    "therefore the", "this leads to a population", "over time this leads",
    "passed on to future generations", "which means that", "so the result is",
    "consists of", "contains a sugar", "contains a phosphate",
    "adenine always pairs", "cytosine always pairs",
    "always pairs with thymine", "always pairs with guanine",
]

def contains_direct_answer(text, topic_keywords=None):
    t = text.lower()
    for phrase in ANSWER_GIVEAWAY_PHRASES:
        if phrase in t:
            return True
    if topic_keywords:
        for kw in topic_keywords:
            if kw.lower() in t:
                return True
    return False


def looks_like_explanation(text):
    t = text.lower()
    if text.count(',') > 3:
        return True
    for phrase in ["such as", "for example,", "specifically,", "in other words",
                   "that is to say", "including", "namely"]:
        if phrase in t:
            return True
    if t.count(" and ") > 3:
        return True
    return False


def is_repetitive(new_response, previous_tutor_responses):
    for prev in previous_tutor_responses[-3:]:
        ratio = SequenceMatcher(None, new_response.lower(), prev.lower()).ratio()
        if ratio > 0.5:
            return True
    return False


def is_good_tutor_response(text, is_first_turn=False):
    if not text:
        return False
    word_count = len(text.split())
    sentences  = [s.strip() for s in text.split('.') if s.strip()]
    has_q      = '?' in text

    if is_first_turn:
        if not has_q:            return False
        if len(sentences) > 3:  return False
        if text.count('?') > 1: return False

    if word_count > 80:         return False
    if not has_q and word_count > 10:
        return False

    # reject role label leaks in tutor output
    t = text.lower()
    if any(tag in t for tag in ["student:", "user:", "\nstudent\n", "\nuser\n"]):
        return False

    return True


def is_good_student_response(text):
    if not text:
        return False
    t = text.lower()
    if len(text.split()) > 35:
        return False
    if any(tag in t for tag in ["tutor:", "user:", "student:", "tutor just said",
                                  "\ntutor\n", "\nuser\n"]):
        return False
    return True


def is_conclusion(text):
    """Detect when tutor has confirmed the student reached the answer."""
    t = text.lower().strip()
    conclusion_phrases = [
        "you got it", "that's it", "exactly —", "exactly—",
        "you derived it", "well done", "you figured it out",
        "that's correct", "perfect —", "spot on"
    ]
    # it's a conclusion if it contains a conclusion phrase AND has no question
    has_phrase = any(p in t for p in conclusion_phrases)
    has_question = '?' in text
    return has_phrase and not has_question


def is_student_confused(text):
    signals = [
        "idk", "i don't know", "not sure", "confused", "don't get",
        "dont get", "no idea", "still not", "hmm", "lost",
        "i thought", "not really", "what do you mean", "not fully"
    ]
    return any(s in text.lower() for s in signals)


def clean_for_saving(text):
    # strip all [HINT...] and [REVEAL...] bracket variants
    text = re.sub(r'\[HINT[^\]]*\]\s*', '', text)
    text = re.sub(r'\[REVEAL[^\]]*\]\s*', '', text)
    # strip bare "Hint:" lines model sometimes adds on its own
    text = re.sub(r'(?m)^Hint:.*$', '', text)
    # strip "Think about X." nudges
    text = re.sub(r'Think about[^.?!]*\.', '', text)
    return text.strip()


# ============================================
# GENERATE ONE CONVERSATION
# ============================================

def generate_conversation(topic_info, num_turns=None, max_retries=4):
    topic      = topic_info["topic"]
    subject    = topic_info["subject"]
    difficulty = topic_info["difficulty"]
    answer_kws = topic_info.get("answer_keywords", [])

    # use per-topic turn count if set, else default to 8
    if num_turns is None:
        num_turns = topic_info.get("turns", 8)

    starter = random.choice(conversation_starters).format(topic=topic)

    guide = TOPIC_GUIDE.get(topic, f"Guide the student toward understanding {topic} step by step.")
    tutor_prompt = (
        TUTOR_SYSTEM_PROMPT
        + f"\n\nTOPIC PATH FOR THIS CONVERSATION: {topic}\n{guide}\n"
        + "Follow this path. Do not introduce unrelated concepts."
    )

    print(f"\n  Topic    : {topic} ({subject}, {difficulty})")
    print(f"  Starter  : {starter}")

    tutor_messages     = []
    student_messages   = []
    conversation_log   = []
    prev_tutor_turns   = []
    struggle_count     = 0
    hint_levels_used   = []
    question_types_log = []

    # ---- TURN 1: student asks ----
    tutor_messages.append({"role": "user", "content": starter})

    tutor_reply = None
    for attempt in range(max_retries):
        reply = call_ollama(tutor_messages, tutor_prompt)
        fail  = []
        if not is_good_tutor_response(reply, is_first_turn=True): fail.append("length/Q")
        if reply and contains_direct_answer(reply, answer_kws):   fail.append("direct-ans")
        if reply and looks_like_explanation(reply):               fail.append("explanation")
        if reply and is_repetitive(reply, prev_tutor_turns):      fail.append("repetitive")
        if not fail:
            tutor_reply = reply
            break
        print(f"  [RETRY {attempt+1}] T1 tutor: {', '.join(fail)}")

    if not tutor_reply:
        print("  [SKIP] No good first tutor response")
        return None

    print(f"  Tutor : {tutor_reply}")
    tutor_messages.append({"role": "assistant", "content": tutor_reply})
    prev_tutor_turns.append(tutor_reply)
    qtype = tag_question_type(tutor_reply)
    question_types_log.append(qtype)
    conversation_log.append({
        "role": "tutor", "content": clean_for_saving(tutor_reply),
        "turn_number": 1, "hint_level": 0, "question_type": qtype
    })

    student_messages.append({
        "role": "user",
        "content": f"You asked: \"{starter}\". Tutor said: \"{tutor_reply}\". Reply as the student now."
    })

    # ---- ALTERNATING TURNS ----
    for turn in range(num_turns - 1):
        turn_num = turn + 2

        # student
        student_reply = None
        for attempt in range(max_retries):
            reply = call_ollama(student_messages, STUDENT_SYSTEM_PROMPT)
            if is_good_student_response(reply):
                student_reply = reply
                break
            print(f"  [RETRY {attempt+1}] T{turn_num} student failed")

        if not student_reply:
            print(f"  [SKIP] No good student at turn {turn_num}")
            return None

        print(f"  Student: {student_reply}")

        if is_student_confused(student_reply):
            struggle_count += 1
        else:
            struggle_count = 0

        hint_level = min(max(struggle_count - 2, 0), 2)
        hint_levels_used.append(hint_level)

        conversation_log.append({
            "role": "student", "content": clean_for_saving(student_reply),
            "turn_number": turn_num, "hint_level": hint_level, "question_type": None
        })

        student_for_tutor = student_reply
        if struggle_count >= 4:
            student_for_tutor = f"[REVEAL] {student_reply}"
        elif struggle_count == 3:
            student_for_tutor = f"[HINT] {student_reply}"

        tutor_messages.append({"role": "user", "content": student_for_tutor})

        # tutor
        tutor_reply = None
        for attempt in range(max_retries):
            reply = call_ollama(tutor_messages, tutor_prompt)
            fail  = []
            if not is_good_tutor_response(reply):                    fail.append("length/Q")
            if reply and contains_direct_answer(reply, answer_kws):  fail.append("direct-ans")
            if reply and looks_like_explanation(reply):              fail.append("explanation")
            if reply and is_repetitive(reply, prev_tutor_turns):     fail.append("repetitive")
            if not fail:
                tutor_reply = reply
                break
            print(f"  [RETRY {attempt+1}] T{turn_num+1} tutor: {', '.join(fail)}")

        if not tutor_reply:
            print(f"  [SKIP] No good tutor at turn {turn_num+1}")
            return None

        print(f"  Tutor : {tutor_reply}")
        tutor_messages.append({"role": "assistant", "content": tutor_reply})
        prev_tutor_turns.append(tutor_reply)
        qtype = tag_question_type(tutor_reply)
        question_types_log.append(qtype)

        conversation_log.append({
            "role": "tutor", "content": clean_for_saving(tutor_reply),
            "turn_number": turn_num + 1, "hint_level": hint_level, "question_type": qtype
        })

        # stop as soon as tutor concludes — don't let conversation drift into small talk
        if is_conclusion(tutor_reply):
            print("  [DONE] Tutor concluded conversation.")
            break

        student_messages.append({"role": "assistant", "content": student_reply})
        student_messages.append({
            "role": "user",
            "content": f"Tutor said: \"{tutor_reply}\". Reply as the student now."
        })

    return {
        "topic":               topic,
        "subject":             subject,
        "difficulty":          difficulty,
        "opening_question":    starter,
        "conversation":        conversation_log,
        "turn_count":          len(conversation_log),
        "max_struggle_streak": struggle_count,
        "question_types":      question_types_log,
        "hint_levels_used":    hint_levels_used,
    }


# ============================================
# MAIN
# ============================================

def main():
    total_examples  = 500      # change to 500 for final training run
    output_file     = "socratic_dataset.jsonl"

    dataset      = []
    attempts     = 0
    max_attempts = total_examples * 5

    print(f"Model           : gemma2:9b")
    print(f"Generating      : {total_examples} conversations (turns per topic)")
    print(f"Output          : {output_file}\n")

    topic_pool = (topics * ((total_examples // len(topics)) + 2))[:max_attempts]
    random.shuffle(topic_pool)

    for topic_info in topic_pool:
        if len(dataset) >= total_examples:
            break
        attempts += 1
        print(f"\n[{len(dataset)+1}/{total_examples}] attempt {attempts}")

        result = generate_conversation(topic_info)  # turns come from topic definition
        if result:
            dataset.append(result)
            print(f"  [OK] saved: {len(dataset)}")
        else:
            print(f"  [FAILED]")

        time.sleep(0.3)

    with open(output_file, "a") as f:
        for item in dataset:
            f.write(json.dumps(item) + "\n")

    print(f"\n{'='*50}")
    print(f"Done. {len(dataset)}/{total_examples} saved in {attempts} attempts → {output_file}")

    if not dataset:
        return

    avg_turns    = sum(d["turn_count"] for d in dataset) / len(dataset)
    subjects     = {}
    difficulties = {}
    all_qtypes   = {}

    for d in dataset:
        subjects[d["subject"]]        = subjects.get(d["subject"], 0) + 1
        difficulties[d["difficulty"]] = difficulties.get(d["difficulty"], 0) + 1
        for qt in d.get("question_types", []):
            all_qtypes[qt] = all_qtypes.get(qt, 0) + 1

    print(f"\nAvg turns/convo  : {avg_turns:.1f}")
    print(f"Subjects         : {subjects}")
    print(f"Difficulties     : {difficulties}")

    total_q = sum(all_qtypes.values())
    print(f"\nQuestion type distribution:")
    for qt in QUESTION_TYPES:
        count = all_qtypes.get(qt, 0)
        pct   = (count / total_q * 100) if total_q else 0
        flag  = "  ← LOW" if pct < 5 and total_q > 20 else ""
        print(f"  {qt:<28} {count:>4}  ({pct:.1f}%){flag}")


if __name__ == "__main__":
    main()