from pathlib import Path
from app.services.ollama_client import OllamaLLM
from app.utils.json_safety import coerce_json

import string
from pathlib import Path

def build_messages(system_path: str, user_path: str, variables: dict):
    system = Path(system_path).read_text(encoding="utf-8")
    user_tmpl = Path(user_path).read_text(encoding="utf-8")
    user = string.Template(user_tmpl).safe_substitute(variables)
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user}
    ]

def run_evaluator(jd_text: str, resume_text: str, candidate_name: str) -> dict:
    messages = build_messages(
        "app/prompts/evaluator_system.md",
        "app/prompts/evaluator_user.md",
        {
            "jd_text": jd_text,
            "resume_text": resume_text,
            "candidate_name": candidate_name
        }
    )
    llm = OllamaLLM()
    raw = llm.chat_json(messages)
    return coerce_json(raw)
