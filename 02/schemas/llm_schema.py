from pydantic import BaseModel

class SummaryResponse(BaseModel):
    target_type: str
    target_id: int
    summary: str