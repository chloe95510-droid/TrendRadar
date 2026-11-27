
import os
import json
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

def analyze_trend(videos, trend, niche):

    if not videos:
        return "No relevant videos found."

    evidence = []

    for video in videos:
        snippet = video["snippet"]
        stats = video["statistics"]

        evidence.append({
            "title": snippet["title"],
            "description": snippet.get("description", "")[:1000],
            "tags": snippet.get("tags", []),
            "published_at": snippet["publishedAt"],
            "views": stats.get("viewCount"),
            "likes": stats.get("likeCount"),
            "comments": stats.get("commentCount"),
            "url": "https://www.youtube.com/watch?v=" + video["id"]
        })

    prompt = f"""
You are TrendRadar, an AI-powered social media
trend analyst and creative strategist.

Trend: {trend}
Creator niche: {niche}

REAL YOUTUBE VIDEO DATA:
{json.dumps(evidence, ensure_ascii=False)}

Analyze the supplied videos and produce:

## 1. Trend Overview
Summarize the trend and its main characteristics.

## 2. Evidence-Based Insights
Identify patterns across the supplied videos.
Reference specific video titles, URLs and real metrics.

## 3. Viral Mechanism
Explain possible reasons why these videos perform well.
Distinguish observations from hypotheses.

## 4. Meme Formula
Extract a reusable content structure that creators
can adapt to their own niche.

## 5. Personalized Remix Ideas
Generate three original content ideas tailored
to the creator's niche.

Each idea must include:
- Title
- Opening hook
- Content structure
- Why it could work
- Reference video

RULES:
- Ground your analysis in the supplied data.
- Never invent engagement statistics.
- Do not claim to have watched the videos.
- Do not invent visual or audio details.
- Do not treat popularity as proof of causation.
- Do not claim this sample represents the entire niche.
- Be concise, specific and actionable.
"""

    print("\nGenerating trend insights...", flush=True)

    response = client.models.generate_content(
        model="gemini-3.8-flash",
        contents=prompt
    )

    return response.text
