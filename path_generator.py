import json
import os
from urllib.parse import quote_plus

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

MODEL = "gemini-2.5-flash"


def get_client():
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError("GOOGLE_API_KEY is missing. Add it to your .env file.")
    return genai.Client(api_key=api_key)


def build_prompt(topic: str, level: str, hours_per_week: int) -> str:
    return f"""
You are an expert learning-path designer.

Create a learning path for:
- Topic: {topic}
- Current level: {level}
- Time available: {hours_per_week} hours per week

Return 5 to 7 stages in order, from basics to advanced. Each stage must include:
- "stage": the stage number, starting at 1
- "title": a short title
- "description": 1 to 2 sentences on what the learner will learn
- "resources": a list of 2 well-known resource names (prefer free ones)
- "youtube_searches": a list of 2 short YouTube search phrases, one for each resource, that would find a good beginner-friendly video (for example, "Python pandas tutorial for beginners")
- "duration_weeks": a whole number of weeks, based on the weekly hours

Respond with JSON only, in exactly this shape:
{{"path": [{{"stage": 1, "title": "...", "description": "...", "resources": ["...", "..."], "youtube_searches": ["...", "..."], "duration_weeks": 2}}]}}
"""


def youtube_search_url(query: str) -> str:
    return "https://www.youtube.com/results?search_query=" + quote_plus(query)


def generate_learning_path(topic: str, level: str, hours_per_week: int) -> list[dict]:
    client = get_client()

    response = client.models.generate_content(
        model=MODEL,
        contents=build_prompt(topic, level, hours_per_week),
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.4,
        ),
    )

    data = json.loads(response.text)
    path = data["path"]

    # Attach a working YouTube link to each resource
    for stage in path:
        stage["videos"] = []
        for name, search in zip(stage["resources"], stage["youtube_searches"]):
            stage["videos"].append({
                "name": name,
                "url": youtube_search_url(search),
            })

    return path