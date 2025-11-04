Return ONLY JSON in this format:
{
  "QUESTION_REVIEW": {
    "summary": "overall feedback",
    "missing_topics": ["topic_1", "topic_2"],
    "improvement_suggestions": ["suggestion_1", "suggestion_2"]
  },
  "UPDATED_QUESTIONS": [
    "question 1?",
    "question 2?"
  ]
}

JD:
---
$jd_text
---

RESUME (plain text):
---
$resume_text
---

YEARS_OF_EXPERIENCE: $yoe
TIME_LIMIT_MINUTES: 60

ORIGINAL_QUESTIONS:
---
$questions_block
---
