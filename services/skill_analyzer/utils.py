import pickle
import spacy
from transformers import T5ForConditionalGeneration, T5Tokenizer
from torch import no_grad

def extract_skills(resume):
    with open("hhru_skills", "rb") as file:
        hhru_skills = pickle.load(file)
    nlp = spacy.load("./extractor_model/model-best")
    doc = nlp(resume)
    extracted_skills = set()
    for ent in doc.ents:
        item = ent.text
        if "\n" in item:
            item = item.replace("\n", " ")
        extracted_skills.add(item)
    cleared_skills = set()
    for skill in extracted_skills:
        if skill.lower() in hhru_skills:
            cleared_skills.add(skill)
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
    cleared_skills = list(cleared_skills)
    normalized_skills = list(set([answer(skill) for skill in cleared_skills]))
    cleared_normalized_skills = set()
    for skill in normalized_skills:
        if skill.lower() in hhru_skills:
            cleared_normalized_skills.add(skill)
    return list(cleared_normalized_skills)