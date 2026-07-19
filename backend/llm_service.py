import os
from anthropic import AsyncAnthropic
from dotenv import load_dotenv

load_dotenv()
client = AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

SYSTEM_PROMPT = """You are a DSA (Data Structures & Algorithms) interview prep coach.
You will be given a user's LeetCode solve statistics broken down by topic.
Generate a personalized, day-by-day study plan (10-14 days) that:
- Prioritizes their weakest topics first
- Recommends 2-4 specific, well-known LeetCode problems per topic (by name)
- Includes brief reasoning for why each topic matters for interviews
- Ends with a short revision day

Format your response in clean Markdown with headers per day.
"""

async def stream_study_plan(gap_analysis: dict):
    user_message = f"""Here is my LeetCode profile analysis:

Difficulty breakdown: {gap_analysis['difficulty_breakdown']}
Weak topics (solved count): {gap_analysis['weak_topics']}
Strong topics (solved count): {gap_analysis['strong_topics']}

Generate my personalized study plan."""

    async with client.messages.stream(
        model="claude-sonnet-4-6",
        max_tokens=2000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_message}],
    ) as stream:
        async for text in stream.text_stream:
            yield text