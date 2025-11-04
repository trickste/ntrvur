import json
import re
from typing import Dict, Any
from pydantic import BaseModel, Field

from langgraph.graph import StateGraph, START, END
from langchain_community.chat_models import ChatOllama


# =========================================================
# 🧩 STATE DEFINITION (required in LangGraph ≥ 1.0)
# =========================================================
class EvaluationState(BaseModel):
    jd_text: str
    resume_text: str
    ATS_SCORE: float | None = Field(default=None)
    YEARS_OF_EXPERIENCE: int | None = Field(default=None)
    CANDIDATE_NAME: str | None = Field(default=None)


# =========================================================
# 🧰 TOOL DEFINITIONS
# =========================================================

def ats_tool(jd_text: str, resume_text: str) -> dict:
    """Compute ATS compatibility score using cosine similarity."""
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity

    vectorizer = TfidfVectorizer(stop_words="english")
    vectors = vectorizer.fit_transform([jd_text, resume_text])
    score = cosine_similarity(vectors[0:1], vectors[1:2])[0][0]
    return {"ATS_SCORE": round(score * 100, 2)}


def experience_extractor_tool(jd_text: str) -> dict:
    """Extract total years of experience mentioned in a JD."""
    match = re.search(r'(\d+)\s*[-–to]{0,3}\s*(\d+)?\s*year', jd_text, re.IGNORECASE)
    years = int(match.group(2) or match.group(1)) if match else 0
    return {"YEARS_OF_EXPERIENCE": years}


def name_extractor_tool(resume_text: str) -> dict:
    """
    Extract candidate's name intelligently from the resume text.
    Priority:
      1. Look for the first line (usually the name)
      2. Look for 'Name:' prefix patterns
      3. Fallback to email prefix (e.g., john.doe@example.com → John Doe)
    """
    # Clean up text and split
    lines = [ln.strip() for ln in resume_text.strip().splitlines() if ln.strip()]
    first_line = lines[0] if lines else ""

    # Case 1: First line looks like a name (no email, phone, or symbols)
    if (
        len(first_line.split()) <= 4
        and not re.search(r"[@|Email|Phone|LinkedIn|GitHub|www]", first_line, re.I)
        and re.match(r"^[A-Z][a-z]+(\s[A-Z][a-z]+)+$", first_line)
    ):
        return {"CANDIDATE_NAME": first_line.strip()}

    # Case 2: Look for "Name:" or "Full Name:" patterns
    match = re.search(
        r"Name[:\-]?\s*([A-Z][a-z]+(?:\s[A-Z][a-z]+)+)",
        resume_text,
        flags=re.IGNORECASE,
    )
    if match:
        return {"CANDIDATE_NAME": match.group(1).strip()}

    # Case 3: Derive from email (john.doe@example.com → John Doe)
    email_match = re.search(r"([a-zA-Z]+)\.([a-zA-Z]+)@", resume_text)
    if email_match:
        name = f"{email_match.group(1).capitalize()} {email_match.group(2).capitalize()}"
        return {"CANDIDATE_NAME": name}

    # Fallback
    return {"CANDIDATE_NAME": "Candidate"}


# =========================================================
# 🧠 GRAPH NODE IMPLEMENTATIONS
# =========================================================

def ats_node(state: EvaluationState) -> EvaluationState:
    result = ats_tool(state.jd_text, state.resume_text)
    print(f"[ATS] → {result}")
    return state.model_copy(update=result)


def experience_node(state: EvaluationState) -> EvaluationState:
    result = experience_extractor_tool(state.jd_text)
    print(f"[Experience] → {result}")
    return state.model_copy(update=result)


def name_node(state: EvaluationState) -> EvaluationState:
    result = name_extractor_tool(state.resume_text)
    print(f"[Name] → {result}")
    return state.model_copy(update=result)


def llm_finalize_node(state: EvaluationState) -> Dict[str, Any]:
    llm = ChatOllama(model="llama3", temperature=0)
    data = {
        "ATS_SCORE": state.ATS_SCORE,
        "YEARS_OF_EXPERIENCE": state.YEARS_OF_EXPERIENCE,
        "CANDIDATE_NAME": state.CANDIDATE_NAME,
    }

    prompt = f"""
Given the extracted info below, return a clean JSON with fields:
ATS_SCORE, YEARS_OF_EXPERIENCE, CANDIDATE_NAME.

Data:
{json.dumps(data, indent=2)}
    """
    response = llm.invoke(prompt)
    text = response.content.strip()
    print(f"[LLM Finalize Output] → {text}")
    try:
        return json.loads(text)
    except Exception:
        return {"raw_output": text}


# =========================================================
# ⚙️ GRAPH SETUP
# =========================================================

graph = StateGraph(EvaluationState)

# Add nodes
graph.add_node("ATS", ats_node)
graph.add_node("EXPERIENCE", experience_node)
graph.add_node("NAME", name_node)
graph.add_node("FINALIZE", llm_finalize_node)

# Define flow edges
graph.add_edge(START, "ATS")  # ✅ Define entrypoint
graph.add_edge("ATS", "EXPERIENCE")
graph.add_edge("EXPERIENCE", "NAME")
graph.add_edge("NAME", "FINALIZE")
graph.add_edge("FINALIZE", END)

# Compile executable graph
evaluator_graph = graph.compile()


# =========================================================
# 🚀 ENTRYPOINT FUNCTION
# =========================================================

def run_agentic_evaluation(jd_text: str, resume_text: str) -> dict:
    print("\n==== Running LangGraph-based Agentic Evaluator ====\n")
    result = evaluator_graph.invoke(EvaluationState(jd_text=jd_text, resume_text=resume_text))
    print("\n==== LangGraph Evaluation Complete ====\n", result)
    return result
