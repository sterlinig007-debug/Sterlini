import json
from .config import settings

async def explain_with_gemini(prompt: str) -> str:
    if not settings.gemini_api_key:
        return (
            "Gemini is optional in this project. No GEMINI_API_KEY is configured. "
            "The application will continue using its deterministic ACL explanation."
        )
    try:
        from google import genai
        client = genai.Client(api_key=settings.gemini_api_key)
        response = client.models.generate_content(
            model=settings.gemini_model,
            contents=prompt,
        )
        return response.text or "The model returned an empty explanation."
    except Exception as exc:
        return f"Gemini explanation unavailable: {exc}"
