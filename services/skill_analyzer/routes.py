from fastapi import APIRouter, Body
from db import async_session_maker
import pickle
import spacy
import json

from transformers import T5ForConditionalGeneration, T5Tokenizer
from torch import no_grad

router = APIRouter()

@router.post("/", summary="Получить список навыков")
async def get_skills(data=Body()):
    with open("data", "rb") as file:
        all_skills = pickle.load(file)
    nlp = spacy.load("./extractor_model/model-best")
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
    def answer(x, **kwargs):
        inputs = tokenizer(x, return_tensors='pt').to(model.device)
        with no_grad():
            hypotheses = model.generate(**inputs, **kwargs)
        return tokenizer.decode(hypotheses[0], skip_special_tokens=True)
    model = T5ForConditionalGeneration.from_pretrained("cointegrated/rut5-small")
    tokenizer = T5Tokenizer.from_pretrained("cointegrated/rut5-small")
    model = model.from_pretrained("./normalize_model")
    tokenizer = tokenizer.from_pretrained("./normalize_model")
    model.eval()
    skills = list(skills)
    normalized_skills = list(set([answer(skill) for skill in skills]))
    return json.dumps({"message": normalized_skills})
