"""Утилитарные функции для Skill Analyzer.

Содержит:
- извлечение навыков из текста (NER + нормализация)
- извлечение текста из PDF
- поиск учебных курсов по найденным навыкам
"""

import torch
from skill_analyzer.model_manager import model_manager
from pdftext.extraction import plain_text_output
import io
from skill_analyzer.db_methods import find_skills_in_db
import numpy as np


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
    extracted_skills = list(extracted_skills)
    model = model_manager.get_normalize_model()
    tokenizer = model_manager.get_tokenizer()

    def normalize_skills_batch(skills_batch: list[str]) -> list[tuple[str, float]]:
        texts = ["normalize skill: " + skill for skill in skills_batch]
        inputs = tokenizer(
            texts,
            return_tensors='pt',
            padding=True,
            truncation=True
        ).to(model.device)

        with torch.inference_mode():
            # Генерация для всего батча
            hypotheses = model.generate(
                **inputs,
                max_length=32,  # Ограничиваем длину выхода
                num_beams=1,     # Жадная декодинг для скорости
                return_dict_in_generate=True,
                output_scores=True
            )
            
            # Вычисляем confidence для всего батча с помощью numpy
            transition_scores = model.compute_transition_scores(
                hypotheses.sequences,
                hypotheses.scores,
                normalize_logits=True
            )
            
            scores_np = [np.array([float(i) for i in row]) for row in transition_scores]
            scores_np = [row[row >= np.log(0.01)] for row in scores_np]
            
            # Минимальные вероятности для каждого примера в батче
            min_probs = [np.min(row) for row in scores_np]

        results = []
        for i, seq in enumerate(hypotheses.sequences):
            decoded = tokenizer.decode(seq, skip_special_tokens=True)
            results.append((decoded, float(min_probs[i])))
        
        return results

    # Нормализуем каждый навык и возвращаем уникальные значения.
    normalized_skills = set()
    batch_size = 16
    for i in range(0, len(extracted_skills), batch_size):
        batch = extracted_skills[i:i + batch_size]
        batch_results = normalize_skills_batch(batch)
        
        # Фильтруем по порогу уверенности
        for skill, confidence in batch_results:
            if confidence > np.log(0.45):
                normalized_skills.add(skill)
    
    return list(normalized_skills)


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