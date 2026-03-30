from flask import Flask, render_template, request,redirect
from flask_sqlalchemy import SQLAlchemy
from utils.ai_generator import generate_mcq
import PyPDF2

app = Flask(__name__)

# 🔹 Database Config
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///examassist.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
with app.app_context():
    db.create_all()

# 🔹 Model (History Table)
class QuizHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    topic = db.Column(db.String(200))
    score = db.Column(db.Integer)
    total = db.Column(db.Integer)

# 🔹 Home Page
@app.route('/')
def home():
    return render_template('index.html')

# 🔹 Generate Quiz
@app.route('/generate', methods=['POST'])
def generate():
    import PyPDF2

    topic = request.form.get('topic', '').strip()
    difficulty = request.form.get('difficulty', 'easy')

    requested = int(request.form.get('num_questions', 5))

    if requested > 30:
        print("⚠️ Limited to 30 questions for better performance")

    num_questions = min(requested, 30)

    time_limit = int(request.form.get('time_limit', 60))

    pdf_file = request.files.get('pdf_file', None)

    extracted_text = ""

    # 🔥 Extract PDF text (if uploaded)
    if pdf_file and pdf_file.filename != "":
        try:
            reader = PyPDF2.PdfReader(pdf_file)

            for page in reader.pages:
                text = page.extract_text()
                if text:
                    extracted_text += text + "\n"

            print("PDF extracted")

        except Exception as e:
            print("PDF Error:", e)

    # 🔥 Limit size (important)
    extracted_text = extracted_text[:3000]

    # 🔥 Decide input
    if topic and extracted_text:
        final_input = topic + "\n" + extracted_text
    elif extracted_text:
        final_input = extracted_text
    elif topic:
        final_input = topic
    else:
        return "❌ Please enter topic or upload a PDF"

    # 🔥 Generate MCQs
    data = generate_mcq(
        f"{final_input} ({difficulty})",
        num_questions
    )

    return render_template(
        'quiz.html',
        data=data,
        topic="PDF + Topic Quiz" if extracted_text else topic,
        time_limit=time_limit
    )

# 🔹 Submit Quiz + Save History
@app.route('/submit', methods=['POST'])
def submit():
    try:
        topic = request.form.get('topic', 'Quiz')
        total = int(request.form.get('total', 0))

        score = 0
        results = []

        for i in range(total):
            answers = request.form.getlist(f"q{i}")
            user_ans = answers[-1] if answers else "Not Attempted"
            correct_ans = request.form.get(f"correct{i}", "")
            explanation = request.form.get(f"explanation{i}", "")

            if not user_ans:
                user_ans = "Not Attempted"

            # 🔥 NORMALIZATION FIX
            user_clean = (user_ans or "").strip().lower()
            correct_clean = (correct_ans or "").strip().lower()

            if user_clean == correct_clean:
                score += 1
                status = "Correct"
            else:
                status = "Wrong"

            results.append({
                "question_no": i + 1,
                "user_ans": user_ans,
                "correct_ans": correct_ans,
                "status": status,
                "explanation": explanation
            })

        # 🔥 SAVE TO DB SAFE
        try:
            quiz = QuizHistory(topic=topic, score=score, total=total)
            db.session.add(quiz)
            db.session.commit()
        except Exception as db_error:
            print("DB Error:", db_error)

        return render_template(
            'result.html',
            score=score,
            total=total,
            results=results
        )

    except Exception as e:
        print("❌ SUBMIT ERROR:", e)
        return f"<h2>Submit Error:</h2><p>{str(e)}</p>"

# 🔹 History Page
@app.route('/history')
def history():
    try:
        print("🔥 History route hit")

        data = QuizHistory.query.all()

        print("Data fetched:", data)

        total_quizzes = len(data)
        total_score = sum(q.score for q in data)

        avg_score = round(total_score / total_quizzes, 2) if total_quizzes > 0 else 0
        best_score = max((q.score for q in data), default=0)

        return render_template(
            'history.html',
            data=data,
            total_quizzes=total_quizzes,
            avg_score=avg_score,
            best_score=best_score
        )

    except Exception as e:
        print("❌ HISTORY ERROR:", e)
        return f"<h2>History Error:</h2><p>{str(e)}</p>"
    
@app.route('/delete/<int:id>')
def delete(id):
    quiz = QuizHistory.query.get(id)

    if quiz:
        db.session.delete(quiz)
        db.session.commit()

    return redirect('/history')

# 🔹 Run App
if __name__ == '__main__':
    app.run(debug=True)