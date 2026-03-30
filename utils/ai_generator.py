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
            Seed: {seed}

            Return ONLY JSON.

            IMPORTANT:
            - Generate DIFFERENT questions every time
            - Avoid repeating questions
            - Follow difficulty strictly

            Topic: {topic}

            RULES:
            EASY → simple definition-based questions
            MEDIUM → concept + application questions
            HARD → tricky + analytical questions

            Generate EXACTLY {current_batch} MCQs.

            Format:
            {{
              "theory": "clean explanation of topic",
              "questions": [
                {{
                  "question": "...",
                  "options": ["Option A", "Option B", "Option C", "Option D"],
                  "answer": "Option A",
                  "explanation": "..."
                }}
              ]
            }}
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

                # Store theory once
                if not theory:
                    theory = data.get("theory", "")

                # Clean bad theory
                if "User content:" in theory or "Difficulty:" in theory:
                    theory = "This topic covers important concepts. Study definitions, examples, and applications."

                # 🔥 FIX ANSWERS
                for q in data.get("questions", []):

                    # Convert A/B/C/D → actual option
                    if q.get("answer") in ["A", "B", "C", "D"]:
                        idx = ["A", "B", "C", "D"].index(q["answer"])
                        q["answer"] = q["options"][idx]

                    # Handle numeric correct_answer
                    if "correct_answer" in q:
                        idx = int(q["correct_answer"]) - 1
                        q["answer"] = q["options"][idx]

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