from fastapi import APIRouter, Body
from db import async_session_maker
import pickle
import spacy
import json

router = APIRouter(prefix='/skill_analyzer')
                   
@router.post("/", summary="Получить список навыков")
async def get_skills(data=Body()):
    with open("data", "rb") as file:
        all_skills = pickle.load(file)
    nlp = spacy.load("./model/model-best")
    doc = nlp(data['text'])
    possible_skills = set()
    for ent in doc.ents:
        item = ent.text
        if "\n" in item:
            item = item.replace("\n", " ")
        possible_skills.add(item)
    skills = set()
    for skill in possible_skills:
        if skill.lower() in all_skills:
            skills.add(skill)
    skills = list(skills)
    return json.dumps({"message": skills})
