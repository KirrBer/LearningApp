from fastapi import APIRouter, Body
from db_methods import find_skills
from utils import extract_skills


router = APIRouter()

@router.post("/", summary="Получить список навыков")
async def get_skills(data=Body()):
    skills = extract_skills(data['text'])
    response = []
    found_skills = await find_skills(skills)
    found_skills_dict = {Skill.name: Skill.course for Skill in found_skills}
    for skill in skills:
        if skill in list(found_skills_dict.keys()):
            response.insert(0, {"name": skill, "course": found_skills_dict[skill]})
        else:
            response.append({"name": skill, "course": None})
    return response
