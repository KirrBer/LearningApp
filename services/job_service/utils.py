from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from db_methods import get_all_vacancies

def recommendations_sort(resume):

    vacancies = get_all_vacancies()

    # Векторизация
    vectorizer = TfidfVectorizer()
    all_texts = [resume] + [vacancy.description for vacancy in vacancies]
    tfidf_matrix = vectorizer.fit_transform(all_texts)

    # Разделяем матрицы
    resume_vector = tfidf_matrix[0]
    vacancy_vectors = tfidf_matrix[1:]

    # Вычисляем все пары
    similarities = cosine_similarity(resume_vector, vacancy_vectors)
    sim_with_vac = zip(similarities, vacancies).sort(key=lambda x: x[0][0])
    sorted_vacancies = list(map(lambda x: x[1], sim_with_vac))
    return sorted_vacancies