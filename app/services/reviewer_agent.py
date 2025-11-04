import string
from pathlib import Path
from app.services.ollama_client import OllamaLLM
from app.utils.json_safety import coerce_json

def build_messages(system_path: str, user_path: str, variables: dict):
    system = Path(system_path).read_text(encoding="utf-8")
    user_tmpl = Path(user_path).read_text(encoding="utf-8")
    user = string.Template(user_tmpl).safe_substitute(variables)
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user}
    ]

def run_reviewer(jd_text: str, resume_text: str, questions: list[str], years_of_experience: int) -> dict:
    messages = build_messages(
        "app/prompts/reviewer_system.md",
        "app/prompts/reviewer_user.md",
        {
            "jd_text": jd_text,
            "resume_text": resume_text,
            "yoe": years_of_experience,
            "questions_block": "\n".join(f"- {q}" for q in questions)
        }
    )
    llm = OllamaLLM()
    raw = llm.chat_json(messages)
    if not raw.strip():
        raise RuntimeError("Reviewer model returned empty output")
    return coerce_json(raw)
