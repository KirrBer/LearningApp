from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from db_methods import get_all_vacancies
from pdftext.extraction import plain_text_output
import io
import numpy as np
import logging
from job_service.threadpool import threadpool_manager

logger = logging.getLogger(__name__)


async def recommendations_sort(resume: str):
    """
    Сортирует вакансии по релевантности к резюме.
    
    Args:
        resume: Текст резюме
        
    Returns:
        Список отсортированных вакансий
        
    Raises:
        ValueError: При ошибке обработки данных
        Exception: При ошибке доступа к БД
    """
    try:
        # Получение вакансий из БД
        vacancies = await get_all_vacancies()
        
        if not vacancies:
            logger.warning("Не найдено вакансий в БД")
            return []
        
        
        # Векторизация
        try:
            vectorizer = TfidfVectorizer(max_features=5000, stop_words='english')
            all_texts = [resume] + [vacancy.description for vacancy in vacancies]
            tfidf_matrix = await threadpool_manager.run_in_custom_threadpool(vectorizer.fit_transform, all_texts)
        except Exception as e:
            logger.error(f"Ошибка при векторизации текста: {str(e)}")
            raise ValueError(f"Не удалось обработать текст резюме: {str(e)}")
        
        # Разделяем матрицы
        resume_vector = tfidf_matrix[0:1]
        vacancy_vectors = tfidf_matrix[1:]

        # Вычисляем все пары
        try:
            similarities = await threadpool_manager.run_in_custom_threadpool(cosine_similarity, resume_vector, vacancy_vectors)
            similarities = similarities[0]
        except Exception as e:
            logger.error(f"Ошибка при вычислении сходимости: {str(e)}")
            raise ValueError(f"Ошибка при анализе релевантности: {str(e)}")

        top_k = min(50, len(vacancies))
        
        # Обработка случая, когда вакансий меньше чем top_k
        if len(vacancies) <= top_k:
            # Если вакансий меньше чем top_k, сортируем все
            top_indices = np.argsort(similarities)[::-1]
        else:
            # argpartition находит top_k наибольших без полной сортировки
            top_indices = np.argpartition(similarities, -top_k)[-top_k:]
            # Сортируем только выбранные
            top_indices = top_indices[np.argsort(similarities[top_indices])[::-1]]
        
        sorted_vacancies = [vacancies[i] for i in top_indices]
        
        logger.info(f"Успешно обработано резюме, найдено {len(sorted_vacancies)} вакансий")
        return sorted_vacancies
        
    except ValueError:
        raise
    except Exception as e:
        logger.error(f"Неожиданная ошибка при сортировке вакансий: {str(e)}")
        raise


async def extract_text_from_pdf(file) -> str:
    """
    Извлекает текст из загруженного PDF файла.
    
    Args:
        file: Загруженный файл (UploadFile)
        
    Returns:
        Извлеченный текст
        
    Raises:
        ValueError: При ошибке парсинга PDF
    """
    try:
        contents = await file.read()
        
        if not contents:
            raise ValueError("Файл пуст")
        
        try:
            text = plain_text_output(
                io.BytesIO(contents),
                sort=True,
                hyphens=False,
            )
        except Exception as e:
            logger.error(f"Ошибка при парсинге PDF: {str(e)}")
            raise ValueError(f"Не удалось прочитать PDF файл: {str(e)}")
        
        if not text or not text.strip():
            raise ValueError("PDF файл не содержит текста")
        
        logger.info(f"Успешно извлечен текст из PDF ({len(text)} символов)")
        return text
        
    except ValueError:
        raise
    except Exception as e:
        logger.error(f"Неожиданная ошибка при извлечении текста из PDF: {str(e)}")
        raise ValueError(f"Ошибка при обработке PDF файла: {str(e)}")