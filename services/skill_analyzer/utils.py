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
from skill_analyzer.exceptions import (
    ModelInferenceError, 
    PDFExtractionError, 
    DatabaseError
)
import logging

logger = logging.getLogger(__name__)


def extract_skills_from_text(resume: str) -> list[str]:
    """Извлекает навыки из текста и нормализует их.

    Алгоритм:
      1) NER (spaCy) выделяет сущности из текста.
      2) Удаляются переносы строк внутри сущностей.
      3) Нормализация через модель T5 (через `model_manager`).
    
    Args:
        resume: Text to extract skills from
        
    Returns:
        List of normalized skills
        
    Raises:
        ModelInferenceError: If model inference fails
    """
    try:
        # безопасный вызов: игнорируется, если модели уже загружены
        model_manager.load_models()

        try:
            nlp = model_manager.get_extractor_model()
            doc = nlp(resume)
        except Exception as e:
            logger.error(f"Error during NER extraction: {str(e)}")
            raise ModelInferenceError(f"Failed to extract skills with NER model: {str(e)}")

        extracted_skills = set()
        for ent in doc.ents:
            item = ent.text
            if "\n" in item:
                item = item.replace("\n", " ")
            extracted_skills.add(item)
        extracted_skills = list(extracted_skills)

        if not extracted_skills:
            return []

        try:
            model = model_manager.get_normalize_model()
            tokenizer = model_manager.get_tokenizer()
        except Exception as e:
            logger.error(f"Error getting normalize model or tokenizer: {str(e)}")
            raise ModelInferenceError(f"Failed to get normalization models: {str(e)}")

        def normalize_skills_batch(skills_batch: list[str]) -> list[tuple[str, float]]:
            """Normalize a batch of skills using T5 model."""
            try:
                texts = ["приведи к каноническому виду название: " + skill for skill in skills_batch]
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
                    min_probs = [np.min(row) if len(row) > 0 else 0.0 for row in scores_np]

                results = []
                for i, seq in enumerate(hypotheses.sequences):
                    decoded = tokenizer.decode(seq, skip_special_tokens=True)
                    results.append((decoded, float(min_probs[i])))
                
                return results
            except Exception as e:
                logger.error(f"Error during batch normalization: {str(e)}")
                raise ModelInferenceError(f"Failed to normalize skills batch: {str(e)}")

        # Нормализуем каждый навык и возвращаем уникальные значения.
        normalized_skills = set()
        batch_size = 16
        for i in range(0, len(extracted_skills), batch_size):
            batch = extracted_skills[i:i + batch_size]
            try:
                batch_results = normalize_skills_batch(batch)
                
                # Фильтруем по порогу уверенности
                for skill, confidence in batch_results:
                    if confidence > np.log(0.7):  # Порог в лог-пространстве
                        normalized_skills.add(skill)
            except ModelInferenceError:
                raise
            except Exception as e:
                logger.error(f"Error processing batch {i}: {str(e)}")
                raise ModelInferenceError(f"Failed to process skill batch: {str(e)}")
        
        return list(normalized_skills)

    except ModelInferenceError:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in extract_skills_from_text: {str(e)}")
        raise ModelInferenceError(f"Unexpected error during skill extraction: {str(e)}")


async def extract_text_from_pdf(file) -> str:
    """Извлекает текст из загруженного PDF файла.
    
    Args:
        file: UploadFile object
        
    Returns:
        Extracted text from PDF
        
    Raises:
        PDFExtractionError: If PDF text extraction fails
    """
    try:
        contents = await file.read()
        
        if not contents:
            raise PDFExtractionError("PDF file is empty")
        
        try:
            text = plain_text_output(
                io.BytesIO(contents),
                sort=True,
                hyphens=False,
            )
            return text
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {str(e)}")
            raise PDFExtractionError(f"Failed to extract text from PDF: {str(e)}")
            
    except PDFExtractionError:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in extract_text_from_pdf: {str(e)}")
        raise PDFExtractionError(f"Unexpected error during PDF extraction: {str(e)}")


async def find_courses(skills: list[str]) -> list[dict]:
    """Сопоставляет список навыков с курсами из БД.

    Возвращает список словарей вида {name: skill, course: course_or_None}.
    Найденные навыки помещаются в начало списка для удобства.
    
    Args:
        skills: List of skill names
        
    Returns:
        List of dicts with skill names and associated courses
        
    Raises:
        DatabaseError: If database query fails
    """
    try:
        if not skills:
            return []

        try:
            found_skills = await find_skills_in_db(skills)
        except DatabaseError:
            raise
        except Exception as e:
            logger.error(f"Error querying skills in database: {str(e)}")
            raise DatabaseError(f"Failed to query skills from database: {str(e)}")

        found_skills_dict = {}
        try:
            for skill_obj in found_skills:
                if hasattr(skill_obj, 'name') and hasattr(skill_obj, 'course'):
                    found_skills_dict[skill_obj.name] = skill_obj.course
        except Exception as e:
            logger.error(f"Error processing skill objects: {str(e)}")
            raise DatabaseError(f"Failed to process skill data: {str(e)}")

        result = []
        for skill in skills:
            if skill in found_skills_dict:
                result.insert(0, {"name": skill, "course": found_skills_dict[skill]})
            else:
                result.append({"name": skill, "course": None})

        return result

    except DatabaseError:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in find_courses: {str(e)}")
        raise DatabaseError(f"Unexpected error during course lookup: {str(e)}")