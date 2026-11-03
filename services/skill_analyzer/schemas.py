from pydantic import BaseModel, Field

class TextRequest(BaseModel):
    text: str
class SkillResponse(BaseModel):
    name: str
    course: str | None

class PDFAnalysisResponse(BaseModel):
    resume_text: str
    skills: list[SkillResponse]