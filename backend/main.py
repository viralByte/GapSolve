from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Dict, Any

# Your custom module imports
from auth import router as auth_router, get_current_user
from leetcode_client import fetch_leetcode_profile
from analyzer import analyze_gaps
from llm_service import stream_study_plan
from typing import List, Optional

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register the authentication routes
app.include_router(auth_router)

class AnalyzeRequest(BaseModel):
    username: str

class StudyPlanRequest(BaseModel):
    username: str
    selected_topics: Optional[List[str]] = []

@app.post("/analyze")
async def analyze_endpoint(request: AnalyzeRequest, current_user: dict = Depends(get_current_user)):
    # Fetch data and return the gap analysis
    profile = await fetch_leetcode_profile(request.username)
    analysis = analyze_gaps(profile)
    return analysis

@app.post("/study-plan")
async def study_plan_endpoint(request: StudyPlanRequest, current_user: dict = Depends(get_current_user)):
    profile = await fetch_leetcode_profile(request.username)
    gap_analysis = analyze_gaps(profile)
    
    # Pass the selected topics down to the LLM service
    return StreamingResponse(
        stream_study_plan(gap_analysis, request.selected_topics), 
        media_type="text/event-stream"
    )