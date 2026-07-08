"""OpenAI vision integration for food image analysis.

Uses Structured Outputs (JSON schema) so the response is guaranteed valid
JSON matching our item shape. The system prompt instructs the model to be
conservative, flag uncertainty, and never claim exact measurement from a
2D image alone.
"""
import base64
import json

from openai import OpenAI

from app.core.config import settings

SYSTEM_PROMPT = """You are a careful nutrition estimation assistant analysing a single food photo.

Rules:
- Identify each visible distinct food item.
- Estimate quantity (grams or ml) as carefully as possible, but you cannot get an exact
  measurement from a photo alone — state this as an assumption.
- Never pretend precision you don't have. Use conservative, round estimates.
- Provide a confidence score (0-1) per item reflecting your real uncertainty.
- List assumptions you made (e.g. "assumed standard restaurant portion", "oil/butter not visible
  but typical for this dish").
- State explicitly when micronutrient values are uncertain (set them to your best estimate but
  keep confidence low).
- If you cannot tell something important (e.g. cooking method, hidden ingredients, exact
  cup size), include a clarifying question in improvement_questions.
- Output strict JSON only, matching the provided schema. No prose outside JSON.
"""

JSON_SCHEMA = {
    "name": "food_analysis",
    "schema": {
        "type": "object",
        "properties": {
            "items": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "category": {"type": "string"},
                        "estimated_quantity": {
                            "type": "object",
                            "properties": {
                                "value": {"type": "number"},
                                "unit": {"type": "string"},
                            },
                            "required": ["value", "unit"],
                            "additionalProperties": False,
                        },
                        "calories_kcal": {"type": "number"},
                        "macros": {
                            "type": "object",
                            "properties": {
                                "protein_g": {"type": "number"},
                                "carbs_g": {"type": "number"},
                                "fat_g": {"type": "number"},
                                "fibre_g": {"type": "number"},
                                "sugar_g": {"type": "number"},
                            },
                            "required": ["protein_g", "carbs_g", "fat_g", "fibre_g", "sugar_g"],
                            "additionalProperties": False,
                        },
                        "micronutrients": {
                            "type": "object",
                            "properties": {
                                "sodium_mg": {"type": "number"},
                                "potassium_mg": {"type": "number"},
                                "calcium_mg": {"type": "number"},
                                "iron_mg": {"type": "number"},
                                "vitamin_c_mg": {"type": "number"},
                                "vitamin_d_mcg": {"type": "number"},
                                "folate_mcg": {"type": "number"},
                            },
                            "required": [
                                "sodium_mg", "potassium_mg", "calcium_mg", "iron_mg",
                                "vitamin_c_mg", "vitamin_d_mcg", "folate_mcg",
                            ],
                            "additionalProperties": False,
                        },
                        "confidence": {"type": "number"},
                        "reasoning_summary": {"type": "string"},
                        "assumptions": {"type": "array", "items": {"type": "string"}},
                    },
                    "required": [
                        "name", "category", "estimated_quantity", "calories_kcal",
                        "macros", "micronutrients", "confidence", "reasoning_summary", "assumptions",
                    ],
                    "additionalProperties": False,
                },
            },
            "accuracy_warnings": {"type": "array", "items": {"type": "string"}},
            "improvement_questions": {"type": "array", "items": {"type": "string"}},
        },
        "required": ["items", "accuracy_warnings", "improvement_questions"],
        "additionalProperties": False,
    },
    "strict": True,
}


def _client() -> OpenAI:
    if settings.openai_base_url:
        return OpenAI(base_url=settings.openai_base_url, api_key=settings.openai_api_key)
    return OpenAI(api_key=settings.openai_api_key)


def analyze_image(filepath: str, notes: str = "") -> dict:
    with open(filepath, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")

    user_text = "Analyse this food photo and estimate nutrition."
    if notes:
        user_text += f" Additional context from the user: {notes}"

    client = _client()
    response = client.chat.completions.create(
        model=settings.openai_vision_model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": user_text},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}},
                ],
            },
        ],
        response_format={"type": "json_schema", "json_schema": JSON_SCHEMA},
    )
    content = response.choices[0].message.content
    return json.loads(content)
