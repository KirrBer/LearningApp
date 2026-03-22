from pydantic import BaseModel, Field

class ResumeRequest(BaseModel):
    resume: str


class VacancyResponse(BaseModel):
    id: int
    name: str
    description: str
    employer: str
    salary: str | None
    employment: str | None
    schedule: str | None
    expirience: str | None
    area: str | None