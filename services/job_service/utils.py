from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from db_methods import get_all_vacancies
from pdftext.extraction import plain_text_output
import io
import numpy as np

async def recommendations_sort(resume):

    vacancies = await get_all_vacancies()
    # Векторизация
    vectorizer = TfidfVectorizer()
    all_texts = [resume] + [vacancy.description for vacancy in vacancies]
    tfidf_matrix = vectorizer.fit_transform(all_texts)
    # Разделяем матрицы
    resume_vector = tfidf_matrix[0:1]
    vacancy_vectors = tfidf_matrix[1:]

    # Вычисляем все пары
    similarities = cosine_similarity(resume_vector, vacancy_vectors)[0]

    top_k = 50
    # argpartition находит top_k наибольших без полной сортировки
    top_indices = np.argpartition(similarities, -top_k)[-top_k:]
    # Сортируем только выбранные
    top_indices = top_indices[np.argsort(similarities[top_indices])[::-1]]
    
    sorted_vacancies = [vacancies[i] for i in top_indices]
    
    return sorted_vacancies

async def extract_text_from_pdf(file) -> str:
    """Извлекает текст из загруженного PDF файла."""

    contents = await file.read()
    text = plain_text_output(
        io.BytesIO(contents),
        sort=True,
        hyphens=False,
    )
    return text