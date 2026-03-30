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

        if remaining <= 3:
            current_batch = remaining
        else:
            current_batch = min(batch_size, remaining)

        success = False
        attempts = 0

        while not success and attempts < 3:
            attempts += 1

            prompt = f"""
            Return ONLY VALID JSON.

            STRICT RULES:
            1. Each question must have EXACTLY one correct answer.
            2. The correct answer MUST be factually correct.
            3. The answer MUST EXACTLY match one of the options.
            4. The explanation MUST support the correct answer.
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

                # 🔥 Clean markdown
                content = content.replace("```json", "").replace("```", "")

                match = re.search(r'\{.*\}', content, re.DOTALL)
                if not match:
                    raise Exception("No JSON found")

                data = json.loads(match.group())

                questions = data.get("questions", [])

                for q in questions:

                    options = q.get("options", [])
                    answer = q.get("answer", "").strip()
                    explanation = q.get("explanation", "").strip()

                    # 🔥 Fix answer mapping

                    # Case 1: A/B/C/D
                    if answer in ["A", "B", "C", "D"]:
                        idx = ["A", "B", "C", "D"].index(answer)
                        if idx < len(options):
                            q["answer"] = options[idx]

                    # Case 2: "Option A", "Answer: B"
                    elif isinstance(answer, str):
                        ans = answer.upper().strip()

                        for letter in ["A", "B", "C", "D"]:
                            if ans == letter or ans.endswith(f": {letter}") or ans.endswith(letter):
                                idx = ["A", "B", "C", "D"].index(letter)
                                if idx < len(options):
                                    q["answer"] = options[idx]
                                break

                    # Case 3: numeric index
                    if "correct_answer" in q:
                        try:
                            idx = int(q["correct_answer"]) - 1
                            if idx < len(options):
                                q["answer"] = options[idx]
                        except:
                            pass

                    # 🔥 FINAL SAFETY: ensure answer is valid
                    if q.get("answer") not in options and options:
                        q["answer"] = options[0]

                    # 🔥 Explanation fix
                    if not explanation:
                        q["explanation"] = f"{q['answer']} is the correct answer."
                    else:
                        # Only fix if completely unrelated
                        if q["answer"].lower() not in explanation.lower():
                            q["explanation"] = f"{q['answer']} is the correct answer."

                # ✅ ADD QUESTIONS ONLY ONCE (FIXED)
                all_questions.extend(questions)

                # Store theory once
                if not theory:
                    theory = data.get("theory", "")

                # Clean bad theory
                if not theory or "User content:" in theory:
                    theory = "This topic covers important concepts. Study definitions, examples, and applications."

                success = True

            except Exception as e:
                print(f"Retry {attempts} failed:", e)

                if attempts == 2 and current_batch > 2:
                    current_batch = current_batch // 2

    # 🔥 Shuffle questions
    random.shuffle(all_questions)

    # Final safety
    if len(all_questions) < num_questions:
        print("⚠️ Could not generate full questions")

    return {
        "theory": theory if theory else f"{topic} explanation.",
        "questions": all_questions[:num_questions]
    }