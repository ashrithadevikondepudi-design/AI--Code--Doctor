from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from analyzer.code_review import review_python_code
from analyzer.optimization import optimize_python_code
from analyzer.security import analyze_security
from analyzer.complexity import complexity_analysis
from analyzer.ai_explanation import explain_code
from analyzer.improvement import improve_python_code as improve_code_analysis


# ==========================================
# FASTAPI APP
# ==========================================

app = FastAPI(
    title="AI Code Doctor API",
    description=(
        "AI-powered code review, optimization, security, "
        "complexity analysis and AI explanation"
    ),
    version="1.0.0"
)


# ==========================================
# CORS
# ==========================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==========================================
# REQUEST MODEL
# ==========================================

class CodeRequest(BaseModel):
    code: str


# ==========================================
# HOME
# ==========================================

@app.get("/")
def home():
    return {
        "message": "AI Code Doctor backend is running"
    }


# ==========================================
# CODE REVIEW
# ==========================================

@app.post("/analyze")
def analyze_code(request: CodeRequest):
    return review_python_code(request.code)


# ==========================================
# OPTIMIZATION
# ==========================================

@app.post("/optimize")
def optimize_code(request: CodeRequest):
    return optimize_python_code(request.code)


# ==========================================
# SECURITY
# ==========================================

@app.post("/security")
def security_check(request: CodeRequest):
    return analyze_security(request.code)


# ==========================================
# COMPLEXITY
# ==========================================

@app.post("/complexity")
def complexity_check(request: CodeRequest):
    return complexity_analysis(request.code)


# ==========================================
# AI EXPLANATION
# ==========================================

@app.post("/explain")
def explain_code_endpoint(request: CodeRequest):
    return explain_code(request.code)


# ==========================================
# IMPROVE CODE
# ==========================================

@app.post("/improve")
def improve_code(request: CodeRequest):
    return improve_code_analysis(request.code)