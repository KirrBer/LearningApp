"""Утилитарные функции для Skill Analyzer.

Содержит:
- извлечение навыков из текста (NER + нормализация)
- извлечение текста из PDF
- поиск учебных курсов по найденным навыкам
"""

from torch import no_grad, exp
from skill_analyzer.model_manager import model_manager
from pdftext.extraction import plain_text_output
import io
from skill_analyzer.db_methods import find_skills_in_db


def extract_skills_from_text(resume: str) -> list[str]:
    """Извлекает навыки из текста и нормализует их.

    Алгоритм:
      1) NER (spaCy) выделяет сущности из текста.
      2) Удаляются переносы строк внутри сущностей.
      3) Нормализация через модель T5 (через `model_manager`).
    """

    model_manager.load_models()  # безопасный вызов: игнорируется, если модели уже загружены

    nlp = model_manager.get_extractor_model()
    doc = nlp(resume)

    extracted_skills = set()
    for ent in doc.ents:
        item = ent.text
        if "\n" in item:
            item = item.replace("\n", " ")
        extracted_skills.add(item)

    model = model_manager.get_normalize_model()
    tokenizer = model_manager.get_tokenizer()
    model.eval()

    def normalize(text: str, **kwargs) -> list[str, float]:
        inputs = tokenizer(text, return_tensors='pt').to(model.device)
        with no_grad():
            hypotheses = model.generate(return_dict_in_generate=True, output_scores=True, **inputs, **kwargs)
            transition_scores = model.compute_transition_scores(
                hypotheses.sequences, 
                hypotheses.scores, 
                normalize_logits=True
            )
                
            # Получаем вероятности (exp от лог-вероятностей)
            probs = exp(transition_scores[0])
            probs_mean = probs.mean().item()
        return [tokenizer.decode(hypotheses.sequences[0], skip_special_tokens=True), probs_mean]


    # Нормализуем каждый навык и возвращаем уникальные значения.
    normalized_skills = set()
    for skill in extracted_skills:
        normalized_skill, confidence = normalize("normalize skill: " + skill)
        if confidence > 0.74:  # фильтр по порогу уверенности (можно настроить)
            normalized_skills.add(normalized_skill)
    return normalized_skills


async def extract_text_from_pdf(file) -> str:
    """Извлекает текст из загруженного PDF файла."""

    contents = await file.read()
    text = plain_text_output(
        io.BytesIO(contents),
        sort=True,
        hyphens=False,
    )
    return text


async def find_courses(skills: list[str]) -> list[dict]:
    """Сопоставляет список навыков с курсами из БД.

    Возвращает список словарей вида {name: skill, course: course_or_None}.
    Найденные навыки помещаются в начало списка для удобства.
    """

    result = []
    found_skills = await find_skills_in_db(skills)
    found_skills_dict = {Skill.name: Skill.course for Skill in found_skills}

    for skill in skills:
        if skill in found_skills_dict:
            result.insert(0, {"name": skill, "course": found_skills_dict[skill]})
        else:
            result.append({"name": skill, "course": None})

    return result