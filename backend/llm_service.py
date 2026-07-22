"""
llm_service.py
Handles turning a structured gap analysis into a personalized, streamed study plan.

Supports two providers, switchable via the LLM_PROVIDER env var:
  - "anthropic" (default) -> Claude API, requires ANTHROPIC_API_KEY
  - "gemini"               -> Google Gemini API (has a genuinely free tier),
                              requires GEMINI_API_KEY

Both are exposed through the same stream_study_plan() generator, so main.py
never needs to know which provider is active.
"""

import os
from typing import AsyncGenerator
from pathlib import Path
from dotenv import load_dotenv
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)


PROVIDER = os.getenv("LLM_PROVIDER", "gemini").lower()

SYSTEM_PROMPT = """You are an expert DSA (Data Structures & Algorithms) interview prep coach.

You will be given a user's LeetCode solve statistics broken down by topic and difficulty.

Generate a personalized, day-by-day study plan (8-10 days) that:
- Prioritizes their weakest topics first, and explains briefly why each matters for interviews
- Recommends 2-4 specific, well-known LeetCode problems per topic (use real, commonly known problem names)
- Gradually increases difficulty within each topic (easy -> medium -> hard)
- Includes a final revision/mock-interview day at the end
- Is realistic for someone studying part-time alongside coursework (assume ~1-2 hours/day)

Format the response in clean Markdown with a "Day N" header for each day.
Do not include any preamble before Day 1 -- start directly with the plan.
"""


def _build_user_message(gap_analysis: dict, selected_topics: list) -> str:
    weak = ", ".join(
        f"{t['topic']} ({t['count']} solved)" for t in gap_analysis["weak_topics"]
    ) or "none identified"
    strong = ", ".join(
        f"{t['topic']} ({t['count']} solved)" for t in gap_analysis["strong_topics"]
    ) or "none identified"

    base_msg = f"""Here is my LeetCode profile analysis:
Username: {gap_analysis['username']}
Difficulty breakdown: {gap_analysis['difficulty_breakdown']}
Weak topics: {weak}
Strong topics: {strong}
"""
    
    # If the user selected specific topics in the UI, force the AI to focus ONLY on those
    if selected_topics:
        topics_str = ", ".join(selected_topics)
        base_msg += f"\nCRITICAL INSTRUCTION: I only want to study these specific topics: {topics_str}. Ignore my general weak/strong topics and ONLY generate a plan for {topics_str}."
    else:
        base_msg += "\nGenerate my personalized study plan based on my weakest topics."

    return base_msg

async def stream_study_plan(gap_analysis: dict, selected_topics: list = None) -> AsyncGenerator[str, None]:
    """Yields chunks of text as the study plan is generated, for progressive rendering."""
    try:
        user_message = _build_user_message(gap_analysis, selected_topics or [])

        if PROVIDER == "gemini":
            async for chunk in _stream_gemini(user_message):
                yield chunk
        else:
            async for chunk in _stream_anthropic(user_message):
                yield chunk
                
    except Exception as e:
        # If the backend crashes here, it will type the error out on your frontend!
        yield f"\n\n**Backend Crash Detected:** {str(e)}\n\nCheck your terminal where Uvicorn is running for the full details."

async def _stream_anthropic(user_message: str) -> AsyncGenerator[str, None]:
    from anthropic import AsyncAnthropic

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY is not set but LLM_PROVIDER=anthropic")

    client = AsyncAnthropic(api_key=api_key)

    async with client.messages.stream(
        model="claude-sonnet-4-6",
        max_tokens=2000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_message}],
    ) as stream:
        async for text in stream.text_stream:
            yield text


# ---------------------------------------------------------------------------
# Gemini backend (free-tier fallback)
# ---------------------------------------------------------------------------

async def _stream_gemini(user_message: str) -> AsyncGenerator[str, None]:
    import google.generativeai as genai

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not set but LLM_PROVIDER=gemini")

    genai.configure(api_key=api_key)

    # gemini-2.5-flash is on Google's free tier
    model = genai.GenerativeModel(
        model_name="gemini-2.5-flash",
        system_instruction=SYSTEM_PROMPT
    )
    
    response = await model.generate_content_async(user_message, stream=True)
    
    async for chunk in response:
        if chunk.text:
            yield chunk.text
