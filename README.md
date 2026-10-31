# 🩺 AI Code Doctor

**AI-powered Python Code Review and Optimization Assistant**

AI Code Doctor is a web-based application that helps developers analyze, understand, and improve their Python code using automated analysis and AI-powered explanations.

## 🚀 Features

- 🔍 **Code Review:** Detect syntax errors, possible coding issues, and code quality concerns.
- ⚡ **Optimization:** Identify potential code optimization opportunities.
- 🔐 **Security Analysis:** Detect common security risks such as hard-coded secrets and unsafe `eval()` usage.
- 📊 **Complexity Analysis:** Analyze time and space complexity.
- 🤖 **AI Explanation:** Generate explanations and suggestions for submitted code.
- ✨ **Code Improvement:** Suggest and apply supported Python code improvements.

## 🛠️ Tech Stack

**Frontend**
- Next.js
- React
- TypeScript
- Tailwind CSS
- Monaco Editor

**Backend**
- Python
- FastAPI
- Abstract Syntax Tree (AST)
- OpenAI API (optional)

## 📁 Project Structure

```text
AI-Code-Doctor/
├── app/
│   ├── page.tsx
│   ├── layout.tsx
│   └── globals.css
├── backend/
│   ├── analyzer/
│   │   ├── ai_explanation.py
│   │   ├── code_review.py
│   │   ├── complexity.py
│   │   ├── improvement.py
│   │   ├── optimization.py
│   │   └── security.py
│   └── main.py
├── public/
├── package.json
└── README.md
```

## ⚙️ Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/ashrithadevikondepudi-design/AI--Code--Doctor.git
cd AI--Code--Doctor
```

### 2. Install frontend dependencies

```bash
npm install
```

### 3. Start the frontend

```bash
npm run dev
```

### 4. Set up the backend

```bash
cd backend
python -m pip install fastapi uvicorn pydantic python-dotenv openai
```

### 5. Start the backend

```bash
python -m uvicorn main:app --reload --port 8000
```

## 🌐 Application URLs

- Frontend: http://localhost:3000
- Backend: http://127.0.0.1:8000
- API Documentation: http://127.0.0.1:8000/docs

## 🔒 Security

Never upload API keys, passwords, or `.env` files to GitHub. Keep secrets in environment variables.

## 👩‍💻 Author

**Ashritha**

GitHub: [@ashrithadevikondepudi-design](https://github.com/ashrithadevikondepudi-design)

---

*AI Code Doctor — Making Python code better, one analysis at a time.*