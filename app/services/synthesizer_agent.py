import json
from typing import Dict, Any, List

def merge_evaluator_and_reviewer(evaluator_json: Dict[str, Any], reviewer_json: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merge the evaluator's questions with the reviewer suggestions to produce final updated interview questions.
    """
    # Extract candidate name (first key)
    candidate_name = next(iter(evaluator_json.keys()))
    evaluator_data = evaluator_json[candidate_name]
    reviewer_data = reviewer_json

    ats_score = evaluator_data.get("ATS_SCORE", 0)
    resume_feedback = evaluator_data.get("RESUME_FEEDBACK", {})
    interview_questions = evaluator_data.get("INTERVIEW_QUESTIONS", [])

    updated_questions = reviewer_data.get("UPDATED_QUESTIONS", [])
    improvement_suggestions = reviewer_data.get("QUESTION_REVIEW", {}).get("improvement_suggestions", [])

    # Merge & deduplicate
    all_questions = interview_questions + updated_questions
    all_questions = list(dict.fromkeys(all_questions))  # remove duplicates while preserving order

    final_json = {
        "payload": {
            candidate_name: {
                "ATS_SCORE": ats_score,
                "RESUME_FEEDBACK": resume_feedback,
                "FINAL_QUESTIONS": all_questions,
                "QUESTIONS_REVIEW_SUMMARY": reviewer_data.get("QUESTION_REVIEW", {})
            }
        },
        "review": reviewer_data
    }

    return final_json
