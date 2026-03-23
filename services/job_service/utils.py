from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from db_methods import get_all_vacancies

async def recommendations_sort(resume):

    vacancies = await get_all_vacancies()
    # Векторизация
    vectorizer = TfidfVectorizer()
    all_texts = [resume] + [vacancy.description for vacancy in vacancies]
    tfidf_matrix = vectorizer.fit_transform(all_texts)
    # Разделяем матрицы
    resume_vector = tfidf_matrix[0:1]
    vacancy_vectors = tfidf_matrix[1:]
    # print(resume_vector)
    # print('-----------------------------------')
    # print(vacancy_vectors)

    # Вычисляем все пары
    similarities = cosine_similarity(resume_vector, vacancy_vectors)[0]
    # print(len(similarities), len(vacancies))
    # print(list(zip(similarities, vacancies)))
    sim_with_vac = sorted(list(zip(similarities, vacancies)), key=lambda x: x[0], reverse=True)
    sorted_vacancies = [vac for _, vac in sim_with_vac]
    return sorted_vacancies