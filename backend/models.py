from pydantic import BaseModel

class AnalyzeRequest(BaseModel):
    username: str