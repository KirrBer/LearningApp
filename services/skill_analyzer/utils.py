import pickle
from torch import no_grad
from model_manager import model_manager
from pdftext.extraction import plain_text_output
import io
from db_methods import find_skills_in_db

def extract_skills_from_text(resume):
    with open("hhru_skills", "rb") as file:
        hhru_skills = pickle.load(file)
    nlp = model_manager.get_extractor_model()
    doc = nlp(resume)
    extracted_skills = set()
    for ent in doc.ents:
        item = ent.text
        if "\n" in item:
            item = item.replace("\n", " ")
        extracted_skills.add(item)
    cleared_skills = set(extracted_skills)
    def answer(x, **kwargs):
        inputs = tokenizer(x, return_tensors='pt').to(model.device)
        with no_grad():
            hypotheses = model.generate(**inputs, **kwargs)
        return tokenizer.decode(hypotheses[0], skip_special_tokens=True)
    model = model_manager.get_normalize_model()
    tokenizer = model_manager.get_tokenizer()
    model.eval()
    cleared_skills = list(cleared_skills)
    normalized_skills = list(set([answer("normalize skill: "+skill) for skill in cleared_skills]))
    cleared_normalized_skills = set()
    for skill in normalized_skills:
        if skill.lower() in hhru_skills:
            cleared_normalized_skills.add(skill)
    return list(cleared_normalized_skills)

async def extract_skills_from_pdf(file):
    contents = await file.read()
    
    text = plain_text_output(
        io.BytesIO(contents),
        sort=True,
        hyphens=False
    )
    result = extract_skills_from_text(text)
    return result
async def find_courses(skills):
    result = []
    found_skills = await find_skills_in_db(skills)
    found_skills_dict = {Skill.name: Skill.course for Skill in found_skills}
    for skill in skills:
        if skill in list(found_skills_dict.keys()):
            result.insert(0, {"name": skill, "course": found_skills_dict[skill]})
        else:
            result.append({"name": skill, "course": None})
    return result