from fastapi import APIRouter, Body
from db import async_session_maker
from dao import SkillDAO
from utils import extract_skills


router = APIRouter()

@router.post("/", summary="Получить список навыков")
async def get_skills(data=Body()):
    skills = extract_skills(data['text'])
    response = []
    for skill in skills:
        found = await SkillDAO.find_skill(skill)
        if found:
            response.append(found)
        else:
            response.append({"name": skill, "course": None})
    return response
