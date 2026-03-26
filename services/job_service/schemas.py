from pydantic import BaseModel, Field, ConfigDict

class ResumeRequest(BaseModel):
    resume: str


class VacancyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    description: str
    employer: str
    salary: str | None
    employment: str | None
    schedule: str | None
    experience: str | None
    area: str | None


class ShortVacancyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    employer: str
    salary: str | None
    area: str | None