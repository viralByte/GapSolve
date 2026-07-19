from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

from models import AnalyzeRequest
from leetcode_client import fetch_leetcode_profile
from analyzer import analyze_gaps
from llm_service import stream_study_plan

app = FastAPI(title="DSA Gap Analyzer API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten this to your frontend URL before deploying
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/analyze")
async def analyze(req: AnalyzeRequest):
    """Returns structured gap analysis (non-streaming, fast)."""
    try:
        profile = await fetch_leetcode_profile(req.username)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception:
        raise HTTPException(status_code=502, detail="Could not reach LeetCode")

    gaps = analyze_gaps(profile)
    return gaps

@app.post("/study-plan")
async def study_plan(req: AnalyzeRequest):
    """Streams the personalized study plan as it's generated."""
    try:
        profile = await fetch_leetcode_profile(req.username)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    gaps = analyze_gaps(profile)

    return StreamingResponse(
        stream_study_plan(gaps),
        media_type="text/plain"
    )