from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional

# Your custom module imports
from auth import router as auth_router, get_current_user
from leetcode_client import fetch_full_profile
from analyzer import analyze_gaps
from llm_service import stream_study_plan
from mangum import Mangum
app = FastAPI()

# 2. Add your routes
@app.get("/")
def read_root():
    return {"Hello": "World"}

# 3. Define the Mangum handler LAST
handler = Mangum(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # NOTE: Change "*" to your actual frontend URL later for security!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)


class AnalyzeRequest(BaseModel):
    username: str

class CompareRequest(BaseModel):
    username_a: str
    username_b: str

class StudyPlanRequest(BaseModel):
    username: str
    selected_topics: Optional[List[str]] = []


@app.post("/analyze")
async def analyze_endpoint(request: AnalyzeRequest, current_user: dict = Depends(get_current_user)):
    profile = await fetch_full_profile(request.username)
    return analyze_gaps(profile)


@app.post("/compare")
async def compare_endpoint(request: CompareRequest, current_user: dict = Depends(get_current_user)):
    profile_a = await fetch_full_profile(request.username_a)
    profile_b = await fetch_full_profile(request.username_b)
    return {"a": analyze_gaps(profile_a), "b": analyze_gaps(profile_b)}


@app.post("/study-plan")
async def study_plan_endpoint(request: StudyPlanRequest, current_user: dict = Depends(get_current_user)):
    profile = await fetch_full_profile(request.username)
    gap_analysis = analyze_gaps(profile)
    return StreamingResponse(
        stream_study_plan(gap_analysis, request.selected_topics),
        media_type="text/event-stream"
    )