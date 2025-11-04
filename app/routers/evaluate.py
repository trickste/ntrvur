from fastapi import APIRouter, UploadFile, File, HTTPException
from app.models.schemas import EvaluateResponse
from app.services.pdf_parser import extract_text_from_pdf
from app.services.agentic_evaluator import run_agentic_evaluation
from app.services.evaluator_agent import run_evaluator
from app.services.reviewer_agent import run_reviewer
from app.services.synthesizer_agent import merge_evaluator_and_reviewer
from app.utils.json_safety import coerce_json
import json

router = APIRouter(prefix="/api", tags=["evaluate"])


@router.post("/evaluate", response_model=EvaluateResponse)
async def evaluate(
    jd_file: UploadFile = File(..., description="JD as .txt"),
    resume_pdf: UploadFile = File(..., description="Resume as .pdf")
):
    """
    Step 1: Extract text from JD and Resume.
    Step 2: Run agentic tool orchestration (ATS, Name, Experience).
    Step 3: Use extracted data for evaluator + reviewer stages.
    Step 4: Merge and return structured evaluation output.
    """

    # ------------------------------------------------------------------
    # Validate file types
    # ------------------------------------------------------------------
    if jd_file.content_type not in ("text/plain", "application/octet-stream"):
        raise HTTPException(status_code=400, detail="JD must be a .txt file")
    if resume_pdf.content_type not in ("application/pdf", "application/octet-stream"):
        raise HTTPException(status_code=400, detail="Resume must be a .pdf file")

    # ------------------------------------------------------------------
    # Extract text from uploaded files
    # ------------------------------------------------------------------
    jd_text = (await jd_file.read()).decode("utf-8", errors="ignore")
    resume_bytes = await resume_pdf.read()
    resume_text = extract_text_from_pdf(resume_bytes)

    # ------------------------------------------------------------------
    # Step 1: Run LangChain Agentic MCP Orchestrator
    # ------------------------------------------------------------------
    mcp_output = run_agentic_evaluation(jd_text, resume_text)
    print("\n========= MCP AGENT OUTPUT =========")
    print(mcp_output)
    print("====================================\n")

    # ------------------------------------------------------------------
    # Parse MCP output (handle nested raw_output and code fences)
    # ------------------------------------------------------------------
    if isinstance(mcp_output, dict):
        if "raw_output" in mcp_output:
            text = mcp_output["raw_output"]
            text = text.strip("` \n")  # remove Markdown code fences/backticks
            try:
                mcp_data = json.loads(text)
            except json.JSONDecodeError:
                mcp_data = coerce_json(text)
        else:
            mcp_data = mcp_output
    elif isinstance(mcp_output, str):
        try:
            mcp_data = json.loads(mcp_output)
        except json.JSONDecodeError:
            mcp_data = coerce_json(mcp_output)
    else:
        mcp_data = {}

    # Extract fields with safe defaults
    candidate_name = mcp_data.get("CANDIDATE_NAME", "Candidate")
    years_of_experience = mcp_data.get("YEARS_OF_EXPERIENCE", 3)
    ats_score = mcp_data.get("ATS_SCORE", 0)

    print(f"🧩 Parsed MCP Data → Name: {candidate_name}, YOE: {years_of_experience}, ATS: {ats_score}")

    # ------------------------------------------------------------------
    # Step 2: Run LLM Evaluator
    # ------------------------------------------------------------------
    eval_json = run_evaluator(
        jd_text=jd_text,
        resume_text=resume_text,
        candidate_name=candidate_name
    )

    # Normalize key to ensure ATS + YOE attach properly
    candidate_key = next(iter(eval_json.keys())) if eval_json else candidate_name
    if candidate_key not in eval_json:
        eval_json[candidate_key] = {}

    eval_json[candidate_key]["ATS_SCORE"] = ats_score
    eval_json[candidate_key]["YEARS_OF_EXPERIENCE"] = years_of_experience

    # ------------------------------------------------------------------
    # Step 3: Extract Interview Questions for Review
    # ------------------------------------------------------------------
    try:
        questions = eval_json[candidate_key]["INTERVIEW_QUESTIONS"]
        if not isinstance(questions, list) or len(questions) == 0:
            raise ValueError("INTERVIEW_QUESTIONS missing or invalid.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Evaluator output invalid: {e}")

    # ------------------------------------------------------------------
    # Step 4: Reviewer Agent
    # ------------------------------------------------------------------
    review_json = run_reviewer(
        jd_text=jd_text,
        resume_text=resume_text,
        questions=questions,
        years_of_experience=years_of_experience
    )

    # ------------------------------------------------------------------
    # Step 5: Merge Evaluator + Reviewer
    # ------------------------------------------------------------------
    final_json = merge_evaluator_and_reviewer(eval_json, review_json)

    print("\n========= FINAL MERGED OUTPUT =========")
    print(json.dumps(final_json, indent=2))
    print("========================================\n")

    return final_json
