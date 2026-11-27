import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

system_prompt = """
You are Trend Radar, an AI social media
trend analyst and creative strategist.

Your goal is to help content creators
understand and adapt social media trends.

For every trend, provide:

1. Trend Overview
   Explain the trend in two sentences.

2. Viral Mechanism
   Explain its potential audience appeal.

3. Meme Formula
   Extract a reusable content structure.

4. Personalized Remix Ideas
   Generate exactly three ideas tailored
   to the creator's content niche.

Each idea must include:
- Title
- Hook
- Content structure
- Why it works

Rules:
- Be concise and actionable.
- Avoid generic content suggestions.
- Do not invent engagement statistics.
- Do not claim a trend is currently viral
  without supporting data.
- If the trend is too broad, ask the user
  to provide a more specific trend.
"""

trend = input("Enter a social media trend: ")
niche = input("Enter your content niche: ")

prompt = f"""
Trend: {trend}
Creator niche: {niche}
"""

print("\nAnalyzing trend...", flush=True)

response = client.models.generate_content(
    model="gemini-3.8-flash",
    contents=prompt,
    config=types.GenerateContentConfig(
        system_instruction=system_prompt
    )
)

print(response.text)