import json
import requests
from decouple import config

API_KEY = config("API_KEY", default=None)

if not API_KEY:
    raise ValueError("API_KEY is not set in .env")

URL = "https://api.groq.com/openai/v1/chat/completions"

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
}


def evaluate_resume(resume_text, vacancy):
    prompt = f"""
You are a recruitment assistant.

Compare the resume against the job vacancy and evaluate how well
the candidate matches the requirements.

JOB VACANCY:
{vacancy}

RESUME:
{resume_text}

Use ATS-style evaluation.

Evaluate:
- Required skills
- Relevant experience
- Education
- Technical skills
- Projects
- Job responsibilities
- Other explicitly stated requirements

Give each criterion an appropriate weight and calculate a final score
from 0 to 100.

Classification:
- Score > 75: shortlist
- Score <= 75: reject

Rules:
- Base the evaluation ONLY on the vacancy and resume.
- Do not invent information.
- Do not consider protected characteristics.
- recommendations must be [] when action is "shortlist".
- For rejected candidates, recommendations should contain professional
  improvement suggestions.

Return ONLY valid JSON in exactly this format:

{{
    "score": 85,
    "action": "shortlist/reject",
    "strengths": [
        "Strong Python experience",
        "Good Django knowledge"
    ],
    "weaknesses": [
        "Limited Docker experience"
    ],
    "recommendations": []
}}
"""

    data = {
        "model": "openai/gpt-oss-120b",
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a recruitment assistant. "
                    "Return strictly valid JSON."
                ),
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
    }

    response = requests.post(
        URL,
        headers=HEADERS,
        json=data,
        timeout=60,
    )

    response.raise_for_status()

    result = response.json()

    # Get the LLM's actual response
    content = result["choices"][0]["message"]["content"]

    # Convert JSON string → Python dictionary
    return json.loads(content)