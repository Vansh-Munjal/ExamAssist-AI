# 🧠 ExamAssist AI

An AI-powered exam preparation platform that generates smart MCQs, analyzes performance, and helps students practice effectively.

---

## 🚀 Features

* 📘 **AI-Based Question Generation**

  * Generate MCQs from topic or uploaded PDF
  * Supports Easy / Medium / Hard difficulty

* 📄 **PDF Upload Support**

  * Extracts text from PDF
  * Generates questions automatically

* 📝 **Custom Quiz**

  * Choose number of questions (up to 30)
  * Set custom timer

* ⏱️ **Timer-Based Test**

  * Auto-submit when time ends

* 📊 **Performance Analysis**

  * Score calculation
  * Detailed results (Correct / Wrong + Explanation)

* 🗂️ **Quiz History**

  * View past attempts
  * Delete individual records

---

## 🛠️ Tech Stack

* **Frontend:** HTML, CSS, JavaScript
* **Backend:** Flask (Python)
* **Database:** SQLite
* **AI Model:** Groq API (LLaMA 3.1)
* **PDF Processing:** PyPDF2

---

## 📂 Project Structure

```
ExamAssist-AI/
│── app.py
│── requirements.txt
│── Procfile
│── .gitignore
│
├── templates/
│   ├── index.html
│   ├── quiz.html
│   ├── result.html
│   └── history.html
│
├── utils/
│   └── ai_generator.py
│
└── instance/
    └── examassist.db
```

---

## ⚙️ Installation & Setup

### 1️⃣ Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/ExamAssist-AI.git
cd ExamAssist-AI
```

---

### 2️⃣ Create virtual environment

```bash
python -m venv venv
source venv/bin/activate   # Mac/Linux
venv\Scripts\activate      # Windows
```

---

### 3️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

---

### 4️⃣ Setup environment variables

Create a `.env` file:

```
GROQ_API_KEY=your_api_key_here
```

---

### 5️⃣ Run the app

```bash
python app.py
```

Open:

```
http://127.0.0.1:5000
```

---

## 🌐 Deployment

Deployed on:

* Render (Backend)
* GitHub (Code hosting)

---

## 🎯 How It Works

1. Enter a topic or upload a PDF
2. AI extracts key content
3. Generates MCQs dynamically
4. User attempts quiz
5. System evaluates + stores results

---

## 🔥 Future Improvements

* 📊 Advanced analytics dashboard
* 🧠 Adaptive difficulty (based on performance)
* 📱 Mobile responsive UI
* 📄 Support for DOCX & images
* 🤖 Chatbot for doubt solving

---

## 👨‍💻 Author

**Vansh Munjal**
🚀 B.Tech CSE | AI/ML Enthusiast | Full Stack Developer

---

## ⭐ Show Your Support

If you like this project, give it a ⭐ on GitHub!
