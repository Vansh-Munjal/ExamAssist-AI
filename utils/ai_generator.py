import json
import os
import re
import random
from dotenv import load_dotenv
from groq import Groq

# 🔹 Load environment variables
load_dotenv()

# 🔹 Initialize Groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def generate_mcq(topic, num_questions):
    all_questions = []
    theory = ""

    batch_size = 5 if num_questions > 30 else 10

    for i in range(0, num_questions, batch_size):

        remaining = num_questions - len(all_questions)

        # Avoid tiny unstable batches
        if remaining <= 3:
            current_batch = remaining
        else:
            current_batch = min(batch_size, remaining)

        success = False
        attempts = 0

        while not success and attempts < 3:
            attempts += 1

            # 🔥 Random seed (for variation)
            seed = random.randint(1, 100000)

            prompt = f"""
            Return ONLY VALID JSON.

            STRICT RULES:
            1. Each question must have EXACTLY one correct answer.
            2. The correct answer MUST be factually correct.
            3. The answer MUST EXACTLY match one of the options.
            4. The explanation MUST match the correct answer.
            5. Do NOT contradict yourself.

            Format:
            {{
            "theory": "...",
            "questions": [
                {{
                "question": "...",
                "options": ["A", "B", "C", "D"],
                "answer": "exact option text",
                "explanation": "must support the correct answer"
                }}
            ]
            }}

            Topic: {topic}
            Generate EXACTLY {current_batch} questions.
            """
            try:
                response = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7,
                    max_tokens=2000
                )

                content = response.choices[0].message.content

                # 🔥 Remove markdown
                content = content.replace("```json", "").replace("```", "")

                match = re.search(r'\{.*\}', content, re.DOTALL)
                if not match:
                    raise Exception("No JSON found")

                data = json.loads(match.group())

                # ✅ ADD THIS BLOCK HERE
                for q in data.get("questions", []):

                    options = q.get("options", [])
                    answer = q.get("answer", "")
                    explanation = q.get("explanation", "").lower()

                    # 🔥 Fix invalid answer
                    if answer not in options and options:
                        q["answer"] = options[0]

                    # 🔥 Fix mismatch
                    if answer and explanation and answer.lower() not in explanation:
                        q["explanation"] = f"{answer} is the correct answer."

                # 👇 THIS SHOULD COME AFTER
                all_questions.extend(data.get("questions", []))

                # Store theory once
                if not theory:
                    theory = data.get("theory", "")

                # Clean bad theory
                if "User content:" in theory or "Difficulty:" in theory:
                    theory = "This topic covers important concepts. Study definitions, examples, and applications."

                # 🔥 FIX ANSWERS
                for q in data.get("questions", []):

                    options = q.get("options", [])

                    # 🔥 Case 1: A/B/C/D
                    if q.get("answer") in ["A", "B", "C", "D"]:
                        idx = ["A", "B", "C", "D"].index(q["answer"])
                        if idx < len(options):
                            q["answer"] = options[idx]

                    # 🔥 Case 2: "Option A", "Answer: B"
                    elif isinstance(q.get("answer"), str):
                        ans = q["answer"].strip().upper()

                        for letter in ["A", "B", "C", "D"]:
                            if letter in ans:
                                idx = ["A", "B", "C", "D"].index(letter)
                                if idx < len(options):
                                    q["answer"] = options[idx]
                                break

                    # 🔥 Case 3: numeric correct_answer
                    if "correct_answer" in q:
                        try:
                            idx = int(q["correct_answer"]) - 1
                            if idx < len(options):
                                q["answer"] = options[idx]
                        except:
                            pass

                    # 🔥 FINAL SAFETY
                    if q.get("answer") not in options and options:
                        q["answer"] = options[0]

                    # Ensure explanation exists
                    if "explanation" not in q:
                        q["explanation"] = "No explanation provided."

                all_questions.extend(data.get("questions", []))

                success = True

            except Exception as e:
                print(f"Retry {attempts} failed:", e)

                # Try smaller batch if failing
                if attempts == 2 and current_batch > 2:
                    current_batch = current_batch // 2

    # 🔥 Shuffle questions for randomness
    random.shuffle(all_questions)

    # Final safety check
    if len(all_questions) < num_questions:
        print("⚠️ Could not generate full questions")

    return {
        "theory": theory if theory else f"{topic} explanation.",
        "questions": all_questions[:num_questions]
    }