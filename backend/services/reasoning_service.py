import requests
import os

def generate_video_reasoning(full_text: str, claims_data: list) -> str:
    """
    Generates AI-powered reasoning for the video content based on its transcript 
    and the claim-verification results.
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return "AI Reasoning is currently unavailable: GROQ_API_KEY not set in environment or .env file."
        
    url = "https://api.groq.com/openai/v1/chat/completions"


    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    claims_summary = ""
    if claims_data:
        for idx, item in enumerate(claims_data, 1):
            claim = item.get('original_claim', '')
            verdict_info = item.get('verdict', {})
            verdict = verdict_info.get('verdict', 'No Verdict')
            confidence = verdict_info.get('confidence', 0.0)
            claims_summary += f"Claim {idx}: \"{claim}\"\nVerdict: {verdict} (Similarity/Confidence Score: {confidence:.2f})\n\n"
    else:
        claims_summary = "No healthcare claims were extracted using basic keyword triggers."

    prompt = f"""
You are an expert Medical Fact-Checking AI system. Your task is to analyze the following data from a video analysis and provide a concise, structured reasoning.

---
FULL TRANSCRIPT (Truncated if too long):
{full_text[:3000]}
...

---
EXTRACTED CLAIMS & SYSTEM VERDICTS:
{claims_summary}

---
INSTRUCTIONS FOR REASONING:
1. **Health Content Status**: Advise if the video actually contains substantive medical or healthcare advice/claims. If it does NOT, explicitly state so (e.g., "This video contains no significant healthcare topics").
2. **Overall Safety & Accuracy Verdict**: Give brief reasoning summarizing the safety and credibility of the video contents based on the verdicts.
3. **Detected Errors/False Claims**: If any claim is suspicious, unsupported, or contradicted by medical standards, highlight which one and why.
4. **Final Recommendation**: Give the viewer direct guidance on how to treat the information presented (e.g., consult a physician).

Respond with a well-formatted markdown response (using lists and bold text for easy reading on a dashboard UI). Do not list exact confidence scores in the final summary unless specifically relevant. Keep it actionable and easy to read.
"""

    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3,
        "max_tokens": 1000
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        result = response.json()
        return result['choices'][0]['message']['content']
    except Exception as e:
        print(f"Groq API Error: {e}")
        return f"Could not generate AI reasoning at this time due to an API issue: {e}"
