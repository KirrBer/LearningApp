from pydantic import BaseModel, Field

class TextRequest(BaseModel):
    text: str
class SkillResponse(BaseModel):
    name: str
    course: str | None