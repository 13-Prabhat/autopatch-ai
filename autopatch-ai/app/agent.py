import json
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# Initialize OpenAI SDK pointed to Nebius Token Factory
client = OpenAI(
   base_url="https://api.groq.com/openai/v1",
    api_key=os.getenv("GROQ_API_KEY"),
)

# Open-source NVIDIA Model hosted on Nebius
MODEL_NAME = os.getenv("NEBIUS_MODEL_NAME", "nebius/nvidia/Nemotron-3-Super-120b-a12b")


def analyze_code_diff(filename: str, diff_content: str) -> dict:
    """
    Sends the Git diff to NVIDIA Nemotron on Nebius Token Factory
    and returns structured feedback with a suggested patch.
    """
    system_prompt = (
        "You are an expert Security Engineer and Lead Developer reviewing Pull Requests. "
        "Analyze code changes for security flaws, performance issues, logic bugs, and edge cases. "
        "You must respond ONLY in raw valid JSON without markdown formatting backticks."
    )

    user_prompt = f"""
Analyze the following diff for file `{filename}` and generate a fix if issues are detected.

Git Diff:
```diff
{diff_content}
```

Respond with this exact JSON schema:
{{
  "has_issues": true,
  "summary": "Brief explanation of bugs/vulnerabilities detected.",
  "review_comment": "Detailed markdown explanation for GitHub PR comment.",
  "fixed_content": "Full corrected file content if has_issues is true, else null"
}}
"""

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.1,
    )

    raw_output = response.choices[0].message.content.strip()

    # Strip code block markdown wrappers if outputted
    if raw_output.startswith("```json"):
        raw_output = raw_output[7:]
    if raw_output.startswith("```"):
        raw_output = raw_output[3:]
    if raw_output.endswith("```"):
        raw_output = raw_output[:-3]

    return json.loads(raw_output.strip())
