Return ONLY JSON in this exact format:

{
  "$candidate_name": {
    "ATS_SCORE": <int>,
    "RESUME_FEEDBACK": {
      "skill_1": "feedback_1",
      "skill_2": "feedback_2",
      ...
    },
    "INTERVIEW_QUESTIONS": [
      "question",
      "question",
      ...
    ]
  }
}

Here is the JOB DESCRIPTION (JD):
---
{jd_text}
---

Here is the RESUME (plain text):
---
{resume_text}
---

INTERVIEWEE_NAME: $candidate_name

Remember:
- Extract all key skills from the JD and provide coverage for each under RESUME_FEEDBACK.
- Generate 10–15 interview questions total.
- Do not include explanations or extra commentary.
- Return valid JSON only.
