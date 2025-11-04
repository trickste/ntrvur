import json, re

def coerce_json(text: str) -> dict:
    cleaned = text.strip()
    # remove code fences or preambles
    cleaned = re.sub(r"^```(json)?", "", cleaned).strip()
    cleaned = re.sub(r"```$", "", cleaned).strip()
    # remove text before first '{'
    if "{" in cleaned:
        cleaned = cleaned[cleaned.find("{"):]
    # fix double braces {{ -> {
    cleaned = cleaned.replace("{{", "{").replace("}}", "}")
    # remove trailing commas
    cleaned = re.sub(r",(\s*[}\]])", r"\1", cleaned)
    return json.loads(cleaned)
